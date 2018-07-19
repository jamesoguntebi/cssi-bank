import jinja2
import os
import webapp2
from datetime import date, datetime
from google.appengine.ext import ndb
from models import User, Transaction

jinja_current_directory = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = False)

"""
Reads transactions from the database, then creates a string of html for adding
transactions to the page. If used, the Jinja environment must be configured to
disable autoescaping.
"""
def build_transactions_html():
    transactions_html = ""

    for transaction in Transaction.query().fetch():
        amount_for_html = transaction.amount
        if transaction.type == "withdraw" or transaction.type == "transfer":
            amount_for_html *= -1

        transactions_html += \
            """
              <div class="transaction">
                <label>{timestamp}</label>
                <label>{amount}</label>
                <label>{other_account}</label>
              </div>
            """.format(
                timestamp = transaction.timestamp,
                amount = amount_for_html,
                other_account = transaction.other_user_name
            )

    return transactions_html

"""
Gets the User object from the database that stores the balance.
"""
def get_or_create_user():
    # If no user exists yet, create one.
    users = User.query().fetch()
    if len(users) == 0:
        user = User()
        user.put()
        return user;

    else:
        return users[0]


class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = get_or_create_user()

        template_dict = {
            "transactions_html": build_transactions_html(),
            "balance": user.balance
        }
        account_home_template = jinja_current_directory.get_template('templates/account_home.html')
        self.response.write(account_home_template.render(template_dict))

    def post(self):
        if self.request.get("type") == "deposit":
            self.doDeposit()
            return
        elif self.request.get("type") == "withdraw":
            self.doWithdrawal()
            return
        elif self.request.get("type") == "transfer":
            self.doTransfer()
            return

    def doDeposit(self):
        user = get_or_create_user()
        amount = float(self.request.get("deposit_amount"))

        new_transaction = Transaction(type = "deposit", amount = amount)
        new_transaction.put()

        user.balance += amount
        user.put()

        self.redirect('/')

    def doWithdrawal(self):
        user = get_or_create_user()
        amount = float(self.request.get("withdraw_amount"))

        new_transaction = Transaction(type = "withdraw", amount = amount)
        new_transaction.put()

        user.balance -= amount
        user.put()

        self.redirect('/')

    def doTransfer(self):
        user = get_or_create_user()
        amount = float(self.request.get("transfer_amount"))

        new_transaction = Transaction(
            type = "transfer",
            amount = amount,
            other_user_name = self.request.get("recipient")
        )
        new_transaction.put()

        user.balance -= amount
        user.put()

        self.redirect('/')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
