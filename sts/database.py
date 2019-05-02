from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# import arrow

# import enums
# import models


class DataAccessLayer:
    def __init__(self):
        self.engine = None
        self.conn_string = "sqlite:///db.db"

    def connect(self):
        self.engine = create_engine(self.conn_string)
        # models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        # models.Base.query = self.session.query_property()

    def get_session(self):
        return self.Session()


dal = DataAccessLayer()

# def init_db(self):
#     models.Base.metadata.drop_all(bind=self.engine)
#     models.Base.metadata.create_all(bind=self.engine)

#     s = self.Session()

#     user = models.User(
#         first_name="Joe",
#         last_name="Black",
#         email="joe2@example.com",
#         cell_phone="+14155552671",
#         identities=[models.Identity(subject="fixture")],
#         notification_policy=models.NotificationPolicy(),
#         financial_details=models.FinancialDetails(subject="cust_3ddxx345"),
#         contexts=[
#             models.Participant(
#                 profile=models.UserProfile(
#                     display_name="Big J",
#                     avatar="http://example.com/me.jpg",
#                     bio="My bio! \n Good stuff to come!!",
#                 )
#             ),
#             models.Facilitator(
#                 profile=models.UserProfile(
#                     display_name="Dr J",
#                     avatar="http://example.com/dr-j.jpg",
#                     bio="Not much to say!",
#                 ),
#                 licenses=[models.License(number="xxx", us_state=enums.UsState.NY)],
#             ),
#             # models.Company(
#             #     profile=models.UserProfile(
#             #         display_name="Cool Company", avatar="avatar", bio="My bio!"
#             #     )
#             # ),
#             # models.Employee(
#             #     profile=models.UserProfile(
#             #         display_name="Employee 1", avatar="avatar", bio="My bio!"
#             #     )
#             # ),
#         ],
#     )
#     s.add(user)
#     s.commit()

#     # emp = s.query(models.Employee).one()
#     # comp = s.query(models.Company).one()
#     # comp.employees.append(emp)
#     # s.commit()


# if __name__ == "__main__":
#     import database as db
#     import models
#     import arrow
#     import enums

#     dal.connect()
#     dal.init_db()

#     s = dal.Session()

#     user = s.query(models.User).one()
