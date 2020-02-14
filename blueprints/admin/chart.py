from datetime import datetime, timedelta
def prepare_chart(query_object):
    # time_now = datetime.now()
    returnable = []
    amount = 0
    for query_item in query_object:
        item_date = datetime.date(query_item.created_at).strftime("%Y-%m-%d")
        amount += 1
        # if item_date == returnable[-1]['date']:
        #     returnable[-1]['amount'] = amount
        # else:
        #     returnable.append({'date':item_date,'amount':amount})
        if returnable == []:
            # amount = 1
            returnable.append({'date':item_date,'amount':amount})
        elif item_date != returnable[-1]['date']:
            returnable.append({'date':item_date,'amount':amount})
        else:
            # amount += 1
            returnable[-1]['amount'] = amount

        

        # print(returnable)
        # print(returnable[-1])
        # print(returnable[-1].amount)

    #patching empty dates

    date_start = datetime.strptime(returnable[0]['date'],"%Y-%m-%d")
    date_end = datetime.strptime(returnable[-1]['date'],"%Y-%m-%d")
    date_now = datetime.now()

    delta_days = (date_now - date_start).days
    for iter in range(delta_days):
        iter_date = date_start + timedelta(days=iter+1)
        iter_date_str = iter_date.strftime("%Y-%m-%d")
        if iter_date_str not in [ x['date'] for x in returnable ]:
            iter_date_before_str = (iter_date - timedelta(days=1)).strftime("%Y-%m-%d")
            amount_before = [x['amount'] for x in returnable if x['date'] == iter_date_before_str][0]
            returnable.append({'date':iter_date_str,'amount':amount_before})

    returnable.sort(key=function_date)

    returnable = returnable[-7:]
    return returnable

def function_date(dict_obj):
    return dict_obj['date']