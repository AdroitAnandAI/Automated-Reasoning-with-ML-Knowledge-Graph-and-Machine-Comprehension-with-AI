from grakn.client import GraknClient

with GraknClient(uri="localhost:48555") as client:
    with client.session(keyspace = "globe") as session:
        with session.transaction().read() as transaction:
            query = [
                'match $country isa country, has countrycode "ZWE";' + 
                ' $city isa city, has cityname $cname; $rel (in-country: $city, contains-city: $country)' +
                ' isa has-city; get $cname;'
            ]

            print("\nQuery:\n", "\n".join(query))
            query = "".join(query)

            iterator = transaction.query(query)






            # concept_map = next(iterator)
            # print("ConceptMap Obj: {}".format(concept_map))
            # # print(concept_map.asThing().attributes)

            # # Get Entity Obj from ConceptMap
            # entity = concept_map.get('city').asAttribute().value().toString()

            # print(entity)
            # print(vars(entity))
            # print("Entity Obj: {}".format(entity))
            # print("Entity Id: {}".format(entity.id))
             
            # # Get Entity Attribute Label/Values
            # attrs = entity.attributes()
            # for each in attrs:
            #      print(each.type().label())
            #      print(each.value())

            # print(iterator)
            # answers = [print(ans) for ans in iterator]


            answers = [ans.get("cname") for ans in iterator]
            print(answers)
            result = [ answer.id for answer in answers ]

            for answer in answers:
                print(answer.type().label(), answer.value())
            print("\nResult:\n", result)

            # answers = [ans.get("city") for ans in iterator]
            # print(answers)
            # result = [ answer.id for answer in answers ]

            # for answer in answers:
            #     print(answer.type().__getattribute__('cityname'))
            #     print(answer.type().label())
            # print("\nResult:\n", result)