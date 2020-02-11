from .model import UsersDetail, Users

def create_mini_profile(user_id):
    qry = UsersDetail.query.filter_by(user_id=user_id    ).first()

    check_f_name = qry.first_name
    check_l_name = qry.last_name
    check_photo = qry.photo_url
    username = Users.query.get(user_id).username

    if (check_f_name == None) & (check_l_name == None):
        display_name = username
    elif (check_l_name == None):
        display_name = check_f_name
    elif (check_f_name == None):
        display_name = check_l_name
    else:
        display_name = check_f_name + " " + check_l_name

    if check_photo == None:
        photo_url = "null"
    else:
        photo_url = check_photo

    user_data = {
        'username': username,
        'display_name': display_name,
        'photo_url': photo_url
    }

    return user_data