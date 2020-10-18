from grakn.client import GraknClient

with GraknClient(uri="localhost:48555") as client:
    with client.session(keyspace = "globe") as session:
        with session.transaction().read() as transaction:
            query = [
                'match $country isa country, has countryname $cname,' +
                ' has indepyear $iy, has region "Caribbean"; $iy > 1980; get $cname;'
            ]

             # has indepyear $iy, has population $p, has surfacearea $sc; $sc > 10000; $p < 1000000; get $cname, $p, $sc;

            print("\nQuery:\n", "\n".join(query))
            query = "".join(query)

            iterator = transaction.query(query)


            #can also use compute max like this but will  get only highest value.
            # if you want to find country with maximum lifeexpectancy, then u need
            # to execute 2 queries, first to compute max and 
            # then the above query to "== max"
            #compute max of lifeexpectancy, in country;

            countries = [[ans.get("cname")] for ans in iterator]
            print(countries)
            # result = [ answer.id for answer in answers ]

            for country in countries:
                print(str(country[0].value()))
                # print(": " country[1].value())
            # print("\nResult:\n", result)

            # answers = [ans.get("city") for ans in iterator]
            # print(answers)
            # result = [ answer.id for answer in answers ]

            # for answer in answers:
            #     print(answer.type().__getattribute__('cityname'))
            #     print(answer.type().label())
            # print("\nResult:\n", result)