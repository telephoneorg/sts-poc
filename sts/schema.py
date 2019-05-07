from graphql import GraphQLError
import graphene as gr
from graphene import relay
from graphene_sqlalchemy import (
    SQLAlchemyConnectionField,
    SQLAlchemyObjectType,
    utils,
)

from . import enums
from . import models


UserContextType = gr.Enum.from_enum(enums.UserContextType)
UserContextStatus = gr.Enum.from_enum(enums.UserContextStatus)
IdentityProvider = gr.Enum.from_enum(enums.IdentityProvider)
PaymentProcessor = gr.Enum.from_enum(enums.PaymentProcessor)
LicenseType = gr.Enum.from_enum(enums.LicenseType)
UsState = gr.Enum.from_enum(enums.UsState)


class User(SQLAlchemyObjectType):
    class Meta:
        model = models.User
        interfaces = (relay.Node,)


class UserContext(SQLAlchemyObjectType):
    class Meta:
        model = models.UserContext
        interfaces = (relay.Node,)


class Participant(SQLAlchemyObjectType):
    class Meta:
        model = models.Participant
        interfaces = (relay.Node,)


class Facilitator(SQLAlchemyObjectType):
    class Meta:
        model = models.Facilitator
        interfaces = (relay.Node,)


# class Company(SQLAlchemyObjectType):
#     class Meta:
#         model = models.Company
#         interfaces = (relay.Node,)


# class Employee(SQLAlchemyObjectType):
#     class Meta:
#         model = models.Employee
#         interfaces = (relay.Node,)


class UserProfile(SQLAlchemyObjectType):
    class Meta:
        model = models.UserProfile
        interfaces = (relay.Node,)


class Identity(SQLAlchemyObjectType):
    class Meta:
        model = models.Identity
        interfaces = (relay.Node,)


class NotificationPolicy(SQLAlchemyObjectType):
    class Meta:
        model = models.NotificationPolicy
        interfaces = (relay.Node,)


# class FinancialDetails(SQLAlchemyObjectType):
#     class Meta:
#         model = models.FinancialDetails
#         interfaces = (relay.Node,)


class License(SQLAlchemyObjectType):
    class Meta:
        model = models.License
        interfaces = (relay.Node,)


class Query(gr.ObjectType):
    node = relay.Node.Field()
    me = gr.Field(User)
    # participant = gr.Field(Participant)
    # facilitator = gr.Field(Facilitator)
    # user = gr.Field(User, id=gr.Int(required=True))

    # def resolve_user(self, info, id):
    #     return User.get_query(info).filter(models.User.id == id).one()

    def resolve_me(self, info):
        if info.context.current_jwt:
            if not info.context.current_user:
                raise GraphQLError("No account found")
            return info.context.current_user._get_current_object()

        else:
            raise GraphQLError("User Not authenticated")


class UserFields(gr.AbstractType):
    first_name = gr.String()
    last_name = gr.String()
    cell_phone = gr.String()


class NewUserFields(UserFields):
    first_name = gr.String(required=True)
    last_name = gr.String(required=True)


class UserInput(gr.InputObjectType, UserFields):
    pass


class NewUserInput(gr.InputObjectType, NewUserFields):
    pass


class CreateUser(relay.ClientIDMutation):
    class Input:
        user = gr.Field(lambda: NewUserInput, required=True)
        profile = gr.Field(lambda: UserProfileInput, required=True)
        notification_policy = gr.Field(
            lambda: NotificationPolicyInput, required=True
        )

    ok = gr.Boolean()
    user = gr.Field(User)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        if not info.context.current_jwt:
            raise GraphQLError("User not authenticated")
        if info.context.current_user:
            raise GraphQLError("User already exists")

        session = info.context.session
        current_jwt = info.context.current_jwt

        user = models.User(
            email=current_jwt.get("email"),
            identities=[models.Identity(subject=current_jwt.get("sub"))],
            contexts=[
                models.Participant(
                    profile=models.UserProfile(**data.get("profile", {}))
                )
            ],
            notification_policy=models.NotificationPolicy(
                **data.get("notification_policy", {})
            ),
            financial_details=models.FinancialDetails(),
            **data.get("user"),
        )
        session.add(user)
        session.commit()
        ok = True
        return cls(ok=ok, user=user)


class UpdateUser(relay.ClientIDMutation):
    class Input:
        user = gr.Field(lambda: UserInput)
        notification_policy = gr.Field(lambda: NotificationPolicyInput)
        context_id = gr.ID()
        profile = gr.Field(lambda: UserProfileInput)

    ok = gr.Boolean()
    user = gr.Field(User)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        raise_for_user_auth_errors(info.context)

        session = info.context.session

        current_user = info.context.current_user._get_current_object()

        patch_model(current_user, data.get("user"))
        patch_model(
            current_user.notification_policy, data.get("notification_policy")
        )

        if "profile" in data:
            user_context = get_user_context(
                current_user, data.get("context_id"), info
            )
            patch_model(user_context.profile, data.get("profile"))

        # for key, val in data.get("user", {}).items():
        #     setattr(current_user, key, val)

        # for key, val in data.get("notification_policy", {}).items():
        #     setattr(current_user.notification_policy, key, val)

        session.commit()
        ok = True
        return cls(ok=ok, user=current_user)
        # user = models.User(
        #     email=current_jwt.get("email"),
        #     identities=[models.Identity(subject=current_jwt.get("sub"))],
        #     contexts=[
        #         models.Participant(
        #             profile=models.UserProfile(**data.get("profile"))
        #         )
        #     ],
        #     notification_policy=models.NotificationPolicy(**data.get("notification_policy")),
        #     financial_details=models.FinancialDetails(),
        #     **data.get("user"),
        # )

        # query = User.get_query(info).filter(models.User.id == current_user.id)
        # query = session.query(models.User).filter_by(id=current_user.id)
        # user = query.one_or_none()
        # session.commit()


class UserProfileFields(gr.AbstractType):
    display_name = gr.String()
    avatar = gr.String()
    bio = gr.String()


class UserProfileInput(gr.InputObjectType, UserProfileFields):
    display_name = gr.String()
    avatar = gr.String()
    bio = gr.String()


def get_user_context(user, context_id, info):
    context = relay.Node.get_node_from_global_id(
        info, context_id, only_type=UserContext
    )
    if not context.user_id == user.id:
        raise GraphQLError("User context is invalid")
    return context


def patch_model(model, data=None):
    data = data or dict()
    for key, val in data.items():
        setattr(model, key, val)


def raise_for_user_auth_errors(context):
    if not context.current_jwt:
        raise GraphQLError("User not authenticated")
    if not context.current_user:
        raise GraphQLError("User doesn't exist")


class UpdateUserProfile(relay.ClientIDMutation):
    class Input:
        user_context_id = gr.ID(required=True)
        profile = gr.Field(UserProfileInput, required=True)

    ok = gr.Boolean()
    profile = gr.Field(UserProfile)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        raise_for_user_auth_errors(info.context)

        session = info.context.session
        current_user = info.context.current_user._get_current_object()
        current_user_context = get_user_context(
            current_user, context_id=data.get("user_context_id"), info=info
        )
        profile = current_user_context.profile
        patch_model(profile, data=data.get("profile"))

        session.commit()
        ok = True
        return cls(ok=ok, profile=profile)


class NotificationPolicyFields(gr.AbstractType):
    allow_email = gr.Boolean()
    allow_sms = gr.Boolean()
    allow_marketing = gr.Boolean()


class NotificationPolicyInput(gr.InputObjectType, NotificationPolicyFields):
    pass


class UpdateUserNotificationPolicy(relay.ClientIDMutation):
    Input = NotificationPolicyFields

    ok = gr.Boolean()
    notification_policy = gr.Field(NotificationPolicy)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        raise_for_user_auth_errors(info.context)

        session = info.context.session
        current_user = info.context.current_user._get_current_object()
        notification_policy = current_user.notification_policy

        patch_model(notification_policy, data=data.get("notification_policy"))
        # for key, val in data.get("notification_policy", {}).items():
        #     setattr(notification_policy, key, val)

        session.commit()
        ok = True
        return cls(ok=ok, notification_policy=notification_policy)


class Mutation(gr.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    update_user_profile = UpdateUserProfile.Field()
    update_user_notification_policy = UpdateUserNotificationPolicy.Field()


schema = gr.Schema(
    query=Query,
    mutation=Mutation,
    types=[
        # User,
        # Participant,
        # Facilitator,
        # UserProfile,
        # Identity,
        # NotificationPolicy,
        # License
    ],
)
