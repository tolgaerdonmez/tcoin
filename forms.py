from wtforms import StringField,FloatField,Form,validators

class AddTransaction(Form):
    sender = StringField("Sender",validators=[validators.Length(min=1)])
    receiver = StringField("Receiver",validators=[validators.Length(min=1)])
    input = FloatField("TCoin Amount",validators=[validators.DataRequired()])
    output = FloatField("TCoin Amount",validators=[validators.DataRequired()])

class AddNode(Form):
    address = StringField("Node-Address",validators=[validators.HostnameValidation(require_tld=False,allow_ip=True)])
