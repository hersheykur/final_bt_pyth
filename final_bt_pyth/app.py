from flask import Flask, redirect, url_for, render_template, request, flash

import os
from os.path import join, dirname
from dotenv import load_dotenv
import braintree
from gateway import generate_client_token, transact, find_transaction

app = Flask(__name__)
app.secret_key = "sandbox_jyxybcy8_r7gzzzgwzffzbm9b"

PORT = int(os.environ.get('PORT', 4466))

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

TRANSACTION_REFUND_STATUSES = [ 
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.Settling,
]

@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('new_checkout'))

@app.route('/checkouts/new', methods=['GET'])
def new_checkout():
    client_token = generate_client_token()
    return render_template('checkouts/new.html', client_token=client_token)

@app.route('/refund/ref10', methods=['GET'])
def refund_new():
    return render_template('refund/ref10.html')

@app.route('/checkouts/<transaction_id>', methods=['GET'])
def show_checkout(transaction_id):
    transaction = find_transaction(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your test transaction has been successfully processed. See the Braintree API response and try again.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('checkouts/show.html', transaction=transaction, result=result)

@app.route('/refunds/<transaction_id>', methods=['GET'])
def show_refund(transaction_id):
    transaction = find_transaction(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_REFUND_STATUSES:
        result = {
            'header': 'Successful Refund!',
            'icon': 'refunding',
            'message': 'Your test transaction has been successfully refunded. See the Braintree API response and try again.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
        }

    return render_template('checkouts/reshow.html', transaction=transaction, result=result)


@app.route('/refund', methods=['POST'])
def give_refund(transaction_id):
    transaction = find_transaction(transaction_id)
    result = refund(transaction, "10.00")
    if result.is_success:
        return redirect(url_for('show_refund'),transaction_id=transaction_id)
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('new_checkout'))
    # transaction = find_transaction(transaction_id)
    # result1 = {}
    # if transaction.status in TRANSACTION_REFUND_STATUSES:
    #     result1 = {
    #         'header': 'Sweet Success!',
    #         'icon': 'success',
    #         'message': 'Your test transaction has been successfully processed and click the button below if you would like to refund.'
    #     }
    # else:
    #     result1 = {
    #         'header': 'No Refund, sorry!',
    #         'icon': 'norefund',
    #         'message': 'Your test transaction has a status of ' + transaction.status + '. See the Braintree API response and try again.'
    #     }

    return render_template('refund/reshow.html', transaction=transaction, result=result1)

@app.route('/checkouts', methods=['POST'])
def create_checkout():
    result = transact({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        return redirect(url_for('show_checkout',transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('new_checkout'))

# @app.route('/refund', methods=['POST'])
# def create_refund():
#     result1 = gateway.transaction.refund({
#         "the_transaction_id": transaction
#         "amount": request.form["amount"]
#     })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)