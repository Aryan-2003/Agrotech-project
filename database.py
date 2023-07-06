from sqlalchemy import create_engine, text
import os

db_connection_string = os.environ['DB_CONN_STRING']

engine = create_engine(db_connection_string,
  connect_args={
    "ssl": {
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  })

def register_user(username,email,password):
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO accounts (username,email,password) VALUES ('{}','{}','{}')".format(username,email,password)))


def retrive_hashed_password(email):
  
  with engine.connect() as conn:
    res = conn.execute(text("SELECT password FROM accounts where email='{}'".format(email)))

  return res.all()[0][0]

def store_feedback(email,feedback_given):
  with engine.connect() as conn:
    conn.execute(text("INSERT INTO accounts (email,feedback_given) VALUES ('{}','{}')".format(email,feedback_given)))

# with engine.connect() as conn:
#     conn.execute(text("DELETE FROM accounts"))


# with engine.connect() as conn:
#     res = conn.execute(text("SELECT * FROM accounts"))
#     print(res.all())

# with engine.connect() as conn:
#     res = conn.execute(text("SELECT password FROM accounts where email='aryan@gmail.com'"))
#     print(res.all())

# print(type(retrive_hashed_password('aryan@gmail.com')[0][0]))


# with engine.connect() as conn:
#     conn.execute(text("CREATE TABLE feedbacks (email VARCHAR(100) NOT NULL, feedback_given VARCHAR(1000))"))





