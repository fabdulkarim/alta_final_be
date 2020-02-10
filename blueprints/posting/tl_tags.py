from ..tag.model import Tags
from .model import TopLevels, TopLevelTags
from blueprints import db

def tl_tags_return(tl_id, status=True):
    qry = TopLevelTags.query.filter_by(tl_id=tl_id)
    if status:
        qry = qry.filter_by(deleted=False)

    rows = []
    for que in qry:
        qry2 = Tags.query.filter_by(tag_id=que.tag_id)
        rows.append(qry2.first().name)

    return rows

def tl_tags_post(tl_id, tag_list):
    for tag_iter in tag_list:
        qry = Tags.query.filter_by(name=tag_iter)
        tag_id = qry.first().tag_id 
        tl_tag = TopLevelTags(tl_id, tag_id)
        db.session.add(tl_tag)
    db.session.commit()

#dont forget to add updated_at on top of the function
def tl_tags_put(tl_id, tag_list):
    db_tag_list = tl_tags_return(tl_id)
    db_tag_list_all = tl_tags_return(tl_id, False)

    if tag_list is None:
        input_set = set()
    else:
        #bug, jadinya kalo ada baru malah jadi nambah
        input_set = set(tag_list)

    input_only = input_set - set(db_tag_list)
    db_only = set(db_tag_list) - input_set
    print("input only: ", input_only)
    print("db only: ", db_only)

    for input_iter in input_only:
        qry = Tags.query.filter_by(name=input_iter)
        tag_id = qry.first().tag_id

        #kondisi if existing
        if input_iter in db_tag_list_all:
            qry_reactivate = TopLevelTags.query.filter_by(tag_id=tag_id).first()
            qry_reactivate.deleted = False
            qry_reactivate.updated_at = db.func.now()

        #kondisi mint
        else:
            #ga jadi pakai post di atas
            #karena atas mintanya list of
            tl_tag = TopLevelTags(tl_id, tag_id)

            db.session.add(tl_tag)

    #delete tags on tl_posting
    for db_iter in db_only:
        qry2 = Tags.query.filter_by(name=db_iter)
        tag_id = qry2.first().tag_id

        qry_delete = TopLevelTags.query.filter_by(tag_id=tag_id).first()
        print(qry_delete)
        qry_delete.deleted = True
        qry_delete.updated_at = db.func.now()

    db.session.commit()