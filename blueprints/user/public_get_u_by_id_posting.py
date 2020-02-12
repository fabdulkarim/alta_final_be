from flask_restful import marshal

from ..posting.model import TopLevels, SecondLevels
from ..posting.tl_tags import tl_tags_return
from ..user.mini_profile import create_mini_profile
from sqlalchemy import desc


def PublicWildcardResource(id, content_type, p, rp):
    #add condition
    if content_type in ['article','question']:
        ct = 'top'
    else:
        ct = 'sec'

    #set base query
    if ct == 'top':
        qry = TopLevels.query
        res_field = TopLevels.response_fields
        last = TopLevels.created_at
    else:
        qry = SecondLevels.query
        res_field = SecondLevels.response_fields
        last = SecondLevels.created_at

    qry = qry.filter_by(user_id=id).filter_by(content_type=content_type).filter_by(content_status=0)

    #sort by time in reverse
    qry = qry.order_by(desc(last))

    #prepare query info so similar to home GET
    #count qry result
    total_result = len(qry.all())
    if (total_result % rp != 0) | (total_result == 0):
        total_pages = int(total_result/rp) + 1
    else:
        total_pages = int(total_result/rp)


    #pagination

    offset = (p-1)*rp
    qry = qry.limit(rp).offset(offset)

    query_info = {
        'total_result': total_result,
        'total_pages': total_pages,
        'page_number': p,
        'result_per_pages': rp
    }

    #prepare returnables
    returnable = {'query_info':query_info}
    rows = []
    for que in qry:
        row_dict = {'posting_detail':marshal(que,res_field)}
        row_dict['user_data'] = create_mini_profile(id)
        if ct == 'sec':
            qry2 = TopLevels.query.get(que.parent_id)
            marshal_parent = marshal(qry2, TopLevels.response_fields)
            marshal_parent['user_data'] = create_mini_profile(qry2.user_id)

            sl_amount = SecondLevels.query.filter_by(parent_id=qry2.id).count()

            marshal_parent['sl_amount'] = sl_amount
            
            tags = tl_tags_return(qry2.id)
            
            marshal_parent['tags'] = tags
            row_dict['parent_detail'] = marshal_parent
        elif ct == 'top':
            sl_amount = SecondLevels.query.filter_by(parent_id=que.id).count()
            row_dict['posting_detail']['sl_amount'] = sl_amount
        rows.append(row_dict)

    if ct == 'top':
        returnable['query_data'] = rows
    else:
        second_data = {
            'second_info': {
                'sl_amount': len(rows)
            },
            'second_detail_list': rows
        }

        returnable['second_data'] = second_data

    return returnable