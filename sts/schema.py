from graphql import GraphQLError
import graphene as gr
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType, utils

# from graphene_sqlalchemy.converter import (
#     convert_sqlalchemy_type,
#     get_column_doc,
#     is_column_nullable,
# )
# from sqlalchemy_utils import ArrowType

from . import enums
from . import models


# @convert_sqlalchemy_type.register(ArrowType)
# def convert_column_to_datetime(type, column, registry=None):
#     from graphene.types.datetime import DateTime

#     return DateTime(
#         description=get_column_doc(column), required=not (is_column_nullable(column))
#     )


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


class CreateUser(relay.ClientIDMutation):
    class Input:
        first_name = gr.String(required=True)
        last_name = gr.String(required=True)
        cell_phone = gr.String()

    ok = gr.Boolean()
    user = gr.Field(User)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        # from . import app

        if info.context.current_user:
            raise GraphQLError("User already has an account!")
        if not info.context.current_jwt:
            raise GraphQLError("User not authenticated")

        session = info.context.session
        current_jwt = info.context.current_jwt

        user = models.User(
            email=current_jwt.get("email"),
            identities=[models.Identity(subject=current_jwt.get("sub"))],
            contexts=[
                models.Participant(
                    profile=models.UserProfile(display_name=data.get("first_name"))
                )
            ],
            notification_policy=models.NotificationPolicy(),
            financial_details=models.FinancialDetails(),
            **data,
        )
        session.add(user)
        session.commit()
        ok = True
        return cls(ok=ok, user=user)


class UpdateUser(relay.ClientIDMutation):
    class Input:
        first_name = gr.String()
        last_name = gr.String()
        cell_phone = gr.String()

    ok = gr.Boolean()
    user = gr.Field(User)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        # from .app import app

        if not info.context.current_jwt:
            raise GraphQLError("User not authenticated")
        if not info.context.current_user:
            raise GraphQLError("User doesn't exist")

        session = info.context.session
        user = info.context.current_user._get_current_object()
        for key, val in data.items():
            setattr(user, key, val)
        session.commit()
        # query = User.get_query(info).filter(models.User.id == current_user.id)
        # query = session.query(models.User).filter_by(id=current_user.id)
        ok = True
        # user = query.one_or_none()
        # session.commit()

        return cls(ok=ok, user=user)


# class UpdateUserProfileProfileInput(gr.InputObjectType):
#     display_name = gr.String()
#     avatar = gr.String()
#     bio = gr.String()


class UpdateUserProfile(relay.ClientIDMutation):
    class Input:
        id = gr.ID(required=True)
        display_name = gr.String()
        avatar = gr.String()
        bio = gr.String()

    ok = gr.Boolean()
    profile = gr.Field(UserProfile)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        # from .app import app

        if not info.context.current_jwt:
            raise GraphQLError("User not authenticated")
        if not info.context.current_user:
            raise GraphQLError("User doesn't exist")

        # app.logger.info(f"data: {data}")

        session = info.context.session
        current_user = info.context.current_user._get_current_object()
        profile = relay.Node.get_node_from_global_id(
            info, data.pop("id"), only_type=UserProfile
        )
        # app.logger.info(f"profile: {profile}")
        if profile.user_context.user_id == current_user.id:
            for key, val in data.items():
                setattr(profile, key, val)

            session.commit()
            ok = True
        else:
            ok = False
        return cls(ok=ok, profile=profile)


class UpdateUserNotificationPolicy(relay.ClientIDMutation):
    class Input:
        id = gr.ID(required=True)
        allow_email = gr.Boolean()
        allow_sms = gr.Boolean()
        allow_marketing = gr.Boolean()

    ok = gr.Boolean()
    notification_policy = gr.Field(NotificationPolicy)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **data):
        # from .app import app

        if not info.context.current_jwt:
            raise GraphQLError("User not authenticated")
        if not info.context.current_user:
            raise GraphQLError("User doesn't exist")

        # app.logger.info(f"data: {data}")

        session = info.context.session
        current_user = info.context.current_user._get_current_object()
        notification_policy = relay.Node.get_node_from_global_id(
            info, data.pop("id"), only_type=NotificationPolicy
        )
        # app.logger.info(f"profile: {profile}")
        if notification_policy.user_id == current_user.id:
            for key, val in data.items():
                setattr(notification_policy, key, val)

            session.commit()
            ok = True
        else:
            ok = False
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
