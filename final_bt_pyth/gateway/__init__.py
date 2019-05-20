import os
from dotenv import load_dotenv
import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="r7gzzzgwzffzbm9b",
        public_key="jxcc4fvr2tfkk6x4",
        private_key="09d06befe348a5f2eb2220df45c98709"
    )
)

def generate_client_token():
    return gateway.client_token.generate()

def transact(options):
    return gateway.transaction.sale(options)

def find_transaction(id):
    return gateway.transaction.find(id)

def refund(id, amount):
	return gateway.transaction.refund(id,amount)
