from wtforms import StringField,FloatField,Form,validators

class AddTransaction(Form):
    # sender = StringField("Sender",validators=[validators.Length(min=1)])
    receiver = StringField("Receiver Address",validators=[validators.Length(min=1)])
    input = FloatField("TCoin Amount",validators=[validators.DataRequired()])
    output = FloatField("Transaction Fee",validators=[validators.DataRequired()])

class AddNode(Form):
    address = StringField("Node-Address",validators=[validators.HostnameValidation(require_tld=False,allow_ip=True)])

class WalletLogin(Form):
    private_key = StringField("Private Key")