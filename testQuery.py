from grakn.client import GraknClient

# client = grakn.Grakn(uri = "localhost:48555")
with GraknClient(uri="localhost:48555") as client:
	with client.session(keyspace = "globe") as ses:
		with ses.transaction(grakn.TxType.READ) as transaction:
		    answer_iterator = transaction.query("match $x sub city; get;")

		    for answer in answer_iterator:
		      attr_iterator = answer.map().get("x").attributes()

		      for attr in attr_iterator:
		        print(attr.label())