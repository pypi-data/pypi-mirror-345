from datetime import timedelta, date, datetime
import pymongo

def date_check(mongo_server):
    con123 = pymongo.MongoClient(mongo_server)
    mydb123 = con123['vorys']
    a = '00-00'

    yesterday_slug = date.today() - timedelta(days=1)  # yesterday
    yesterday = yesterday_slug.strftime("%d-%m-%Y")
    dicts = []
    for i in range(48):
        d = f'{yesterday}-{a}_daily'
        dt = datetime.strptime(d, '%d-%m-%Y-%H-%M_daily')
        dt1 = dt + timedelta(minutes=30)
        ddd1 = str(dt1).split()[-1].split(":")[0]
        ddd2 = str(dt1).split()[-1].split(":")[1]
        value = f'{ddd1}-{ddd2}'
        Final_date = f'{yesterday}-{value}_daily'
        a = value

        collection1 = mydb123[f'{Final_date}']

        for doc in collection1.find({}, {"DATETIME": 1, "_id": 0}):
            final_date = doc.get("DATETIME")
            dt = datetime.strptime(final_date, "%m-%d-%YT%H:%M")

            formatted_date = dt.strftime("%d-%m-%Y")
            if formatted_date != yesterday:
                final_return = Final_date + " : " + formatted_date
                dicts.append(final_return)

            else:
                pass

    return dicts