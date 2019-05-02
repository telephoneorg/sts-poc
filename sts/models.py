from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    Table,
    Boolean,
    Unicode,
    UnicodeText,
    DateTime,
)
from sqlalchemy.orm import relationship, backref, validates
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils import generic_repr


from . import enums


def utcnow():
    return datetime.now(timezone.utc)


Base = declarative_base()


class TimestampMixin:
    created = Column(DateTime, nullable=False, default=utcnow)
    updated = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)


@generic_repr
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(Unicode(255), nullable=False)
    last_name = Column(Unicode(255), nullable=False)
    email = Column(Unicode(255), nullable=False, unique=True)
    cell_phone = Column(Unicode(255))

    identities = relationship("Identity", back_populates="user")
    contexts = relationship("UserContext", back_populates="user")
    notification_policy = relationship(
        "NotificationPolicy", back_populates="user", uselist=False
    )
    financial_details = relationship(
        "FinancialDetails", back_populates="user", uselist=False
    )


@generic_repr
class UserContext(Base, TimestampMixin):
    __tablename__ = "user_contexts"
    __mapper_args__ = {"polymorphic_on": "type"}

    id = Column(Integer, primary_key=True)
    type = Column(Enum(enums.UserContextType))
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    status = Column(
        Enum(enums.UserContextStatus),
        nullable=False,
        default=enums.UserContextStatus.CREATED,
    )

    user = relationship("User", back_populates="contexts")
    profile = relationship("UserProfile", uselist=False, back_populates="user_context")
    # communities = relationship("CommunityMember", back_populates="user")
    # groups = relationship("GroupMember", back_populates="user")


@generic_repr
class Participant(UserContext):
    __mapper_args__ = {"polymorphic_identity": enums.UserContextType.PARTICIPANT}


@generic_repr
class Facilitator(UserContext):
    __mapper_args__ = {"polymorphic_identity": enums.UserContextType.FACILITATOR}

    npi = Column(Unicode(255))
    availability = Column(UnicodeText)

    licenses = relationship("License", back_populates="facilitator")


# @generic_repr
# class Employee(Participant):
#     __mapper_args__ = {"polymorphic_identity": enums.UserContextType.EMPLOYEE}

#     company_id = Column(ForeignKey("user_contexts.id"), index=True)
#     company = relationship(
#         "Company", uselist=False, remote_side="Employee.id", back_populates="employees"
#     )

#     @validates("company")
#     def validate_company(self, key, obj):
#         assert isinstance(obj, Company)
#         return obj


# @generic_repr
# class Company(UserContext):
#     __mapper_args__ = {"polymorphic_identity": enums.UserContextType.COMPANY}

#     employees = relationship("Employee", back_populates="company")

#     @validates("employees")
#     def validate_employees(self, key, obj):
#         assert isinstance(obj, Employee)
#         return obj


@generic_repr
class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True)
    user_context_id = Column(ForeignKey("user_contexts.id"), nullable=False, index=True)
    display_name = Column(Unicode(255))
    avatar = Column(Unicode(255))
    bio = Column(UnicodeText)

    user_context = relationship("UserContext", uselist=False, back_populates="profile")


@generic_repr
class Identity(Base, TimestampMixin):
    __tablename__ = "identities"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(
        Enum(enums.IdentityProvider), nullable=False, default=enums.IdentityProvider.CUP
    )
    subject = Column(Unicode(255), nullable=False)

    user = relationship("User", back_populates="identities")


@generic_repr
class NotificationPolicy(Base, TimestampMixin):
    __tablename__ = "notification_policies"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    allow_email = Column(Boolean, default=True)
    allow_sms = Column(Boolean, default=True)
    allow_marketing = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_policy")


@generic_repr
class FinancialDetails(Base, TimestampMixin):
    __tablename__ = "financial_details"

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
    processor = Column(Enum(enums.PaymentProcessor))
    subject = Column(Unicode(255))

    user = relationship("User", back_populates="financial_details")


@generic_repr
class License(Base, TimestampMixin):
    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True)
    facilitator_id = Column(ForeignKey("user_contexts.id"), nullable=False, index=True)
    type = Column(
        Enum(enums.LicenseType), nullable=False, default=enums.LicenseType.TBD
    )
    number = Column(Unicode(255), nullable=False)
    expiry = Column(DateTime)
    us_state = Column(Enum(enums.UsState))

    facilitator = relationship("Facilitator", back_populates="licenses")

    @validates("facilitator")
    def validate_facilitator(self, key, obj):
        assert isinstance(obj, Facilitator)
        return obj


# @generic_repr
# class Community(Base, TimestampMixin):
#     __tablename__ = "communities"

#     id = Column(Integer, primary_key=True)
#     name = Column(Unicode(255), nullable=False)
#     slug = Column(Unicode(255), nullable=False)
#     description = Column(UnicodeText)
#     photo = Column(Unicode(255))
#     cover_photo = Column(Unicode(255))
#     status = Column(Enum(enums.BasicStatus), default=enums.BasicStatus.INACTIVE)

#     groups = relationship("Group", secondary="community_groups")
#     members = relationship("CommunityMember", back_populates="community")


# @generic_repr
# class Recurrence(Base):
#     __tablename__ = "recurrences"

#     id = Column(Integer, primary_key=True)
#     association_id = Column(Integer, ForeignKey("recurrence_associations.id"))
#     start_datetime = Column(ArrowType)
#     end_datetime = Column(ArrowType)
#     period = Column(Enum(enums.TimePeriod), default=enums.TimePeriod.WEEK)
#     interval = Column(Integer, nullable=False, default=1)

#     association = relationship("RecurrenceAssociation", back_populates="recurrence")
#     parent = association_proxy("association", "parent")


# @generic_repr
# class RecurrenceAssociation(Base):
#     __tablename__ = "recurrence_associations"

#     id = Column(Integer, primary_key=True)
#     type = Column(Enum("group", "plan"))

#     recurrence = relationship("RecurrenceAssociation", back_populates="association")


# class HasRecurrence:
#     """HasRecurrence mixin, creates a relationship to
#     the recurrence_associations table for each parent.
#     """

#     @declared_attr
#     def recurrence_association_id(cls):
#         return Column(Integer, ForeignKey("recurrence_associations.id"))

#     @declared_attr
#     def recurrence_association(cls):
#         name = cls.__name__
#         discriminator = name.lower()

#         assoc_cls = type(
#             "%sRecurrenceAssociation" % name,
#             (RecurrenceAssociation,),
#             dict(
#                 __tablename__=None,
#                 __mapper_args__={"polymorphic_identity": discriminator},
#             ),
#         )

#         cls.recurrence = association_proxy(
#             "recurrence_associations",
#             "recurrence",
#             creator=lambda recurrence: assoc_cls(recurrence=recurrence),
#         )
#         return relationship(assoc_cls, backref=backref("parent", uselist=False))


# @generic_repr
# class CommunityMember(Base):
#     __tablename__ = "community_members"

#     community_id = Column(
#         ForeignKey("communities.id"), primary_key=True, nullable=False
#     )
#     user_id = Column(
#         ForeignKey("users.id"), primary_key=True, nullable=False, index=True
#     )
#     joined = Column(ArrowType, nullable=False, default=arrow.utcnow)
#     left = Column(ArrowType)

#     community = relationship("Community", back_populates="members")
#     user = relationship("User", back_populates="communities")


# @generic_repr
# class Group(Base, HasRecurrence, TimestampMixin):
#     __tablename__ = "groups"

#     id = Column(Integer, primary_key=True)
#     facilitator_id = Column(ForeignKey("users.id"), nullable=False, index=True)
#     name = Column(Unicode(255), nullable=False)
#     slug = Column(Unicode(255), nullable=False)
#     description = Column(UnicodeText)
#     photo = Column(Unicode(255))
#     cover_photo = Column(Unicode(255))
#     recurrence_id = Column(ForeignKey("recurrences.id"), nullable=False, index=True)
#     credit_cost = Column(Integer, default=1)

#     # recurrence = relationship("Recurrence", uselist=False)
#     facilitator = relationship("Facilitator", back_populates="groups")
#     participants = relationship("GroupMember", back_populates="group")


# community_groups = Table(
#     "community_groups",
#     Base.metadata,
#     Column(
#         "community_id", ForeignKey("communities.id"), primary_key=True, nullable=False
#     ),
#     Column(
#         "group_id",
#         ForeignKey("groups.id"),
#         primary_key=True,
#         nullable=False,
#         index=True,
#     ),
# )


# @generic_repr
# class GroupMember(Base):
#     __tablename__ = "group_members"

#     group_id = Column(ForeignKey("groups.id"), primary_key=True, nullable=False)
#     participant_id = Column(
#         ForeignKey("users.id"), primary_key=True, nullable=False, index=True
#     )
#     joined = Column(ArrowType, nullable=False, default=arrow.utcnow)
#     left = Column(ArrowType)

#     group = relationship("Group", back_populates="participants")
#     participant = relationship("Participant", back_populates="groups")

#     @validates("participant")
#     def validate_company(self, key, obj):
#         assert isinstance(obj, Participant)
#         return obj


# @generic_repr
# class GroupSession(Base):
#     __tablename__ = "group_sessions"

#     id = Column(Integer, primary_key=True)
#     group_id = Column(ForeignKey("groups.id"), nullable=False, index=True)
#     facilitator_id = Column(ForeignKey("user_profiles.id"), nullable=False, index=True)
#     topic = Column(Unicode(255))
#     description = Column(UnicodeText)

#     facilitator = relationship("UserProfile")
#     group = relationship("Group")
#     participants = relationship("UserProfile", secondary="attended_group_sessions")


# t_attended_group_sessions = Table(
#     "attended_group_sessions",
#     Base.metadata,
#     Column(
#         "group_session_id",
#         ForeignKey("group_sessions.id"),
#         primary_key=True,
#         nullable=False,
#     ),
#     Column(
#         "participant_id",
#         ForeignKey("user_profiles.id"),
#         primary_key=True,
#         nullable=False,
#         index=True,
#     ),
# )


# @generic_repr
# class Order(Base, TimestampMixin):
#     __tablename__ = "orders"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
#     status = Column(
#         Enum(enums.OrderStatus), nullable=False, default=enums.OrderStatus.CREATED
#     )

#     user = relationship("User")


# @generic_repr
# class Product(Base, TimestampMixin):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True)
#     type = Column(Enum(enums.ProductType), nullable=False)
#     name = Column(Unicode(255), nullable=False)
#     slug = Column(Unicode(255), nullable=False)
#     description = Column(UnicodeText)
#     status = Column(
#         Enum(enums.ProductStatus), nullable=False, default=enums.ProductStatus.INACTIVE
#     )
#     credits = Column(Integer, nullable=False, default=1)
#     recurrence_id = Column(ForeignKey("recurrences.id"), index=True)

#     recurrence = relationship("Recurrence")


# @generic_repr
# class Credit(Base):
#     __tablename__ = "credits"

#     id = Column(Integer, primary_key=True)
#     user_id = Column(ForeignKey("users.id"), nullable=False, index=True)
#     # order_id = Column(ForeignKey("orders.id"), index=True)
#     type = Column(Enum(enums.CreditTransactionType), nullable=False)
#     amount = Column(Integer, nullable=False)
#     note = Column(UnicodeText)
#     created = Column(ArrowType, nullable=False, default=arrow.utcnow)

#     # order = relationship("Order")
#     user = relationship("User")


# @generic_repr
# class OrderItem(Base):
#     __tablename__ = "order_items"

#     order_id = Column(ForeignKey("orders.id"), primary_key=True, nullable=False)
#     product_id = Column(
#         ForeignKey("products.id"), primary_key=True, nullable=False, index=True
#     )
#     qty = Column(Integer, nullable=False, default=1)
#     price = Column(Integer, nullable=False)

#     order = relationship("Order")
#     product = relationship("Product")
