from bson.objectid import ObjectId
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

SECRET_KEY = 'hanghae_2_1_7'

# client = MongoClient('localhost', 27017)


db = client.db_hanghae_2_1_7


@app.route('/')
def home():
    matches = list(db.matches.find().sort('cheer_datetime', -1))

    for match in matches:
        match["_id"] = str(match["_id"])

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        return render_template('index.html', user_info=user_info, matches=matches)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

# 월별 경기 조회
@app.route('/<month>')
def home_month(month):
    matches = list(db.matches.find().sort('cheer_datetime', -1))

    for match in matches:
        match["_id"] = str(match["_id"])

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        return render_template('index.html', user_info=user_info, matches=matches, month=month)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 로그인
@app.route('/signin')
def login():
    return render_template('login.html');


# 회원가입 요청
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    user_id = request.form['userId']
    user_pw = request.form['userPw']
    nick_name = request.form['nickName']
    grade = 0
    password_hash = hashlib.sha256(user_pw.encode('utf-8')).hexdigest()
    now = datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')
    doc = {
        "user_id": user_id,
        "user_pw": password_hash,
        "nick_name": nick_name,
        "grade": int(grade),
        "join_date": nowDatetime
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 회원가입 페이지
@app.route('/signUp')
def sign_up_page():
    return render_template('signUp.html')


# 로그인 요청
@app.route('/api/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    userId = request.form['userId']
    userPw = request.form['userPw']

    pw_hash = hashlib.sha256(userPw.encode('utf-8')).hexdigest()
    result = db.users.find_one({'user_id': userId, 'user_pw': pw_hash})

    if result is not None:
        payload = {
            'id': userId,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 아이디 중복체크
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    userId = request.form['userId']
    exists = bool(db.users.find_one({"user_id": userId}))
    return jsonify({'result': 'success', 'exists': exists})


# 상세 페이지
@app.route("/cheer/<matchIdx>", methods=['GET'])
def cheer(matchIdx):
    match = db.matches.find_one({"_id": ObjectId(matchIdx)})
    contents = list(db.contents.find({"match_idx": ObjectId(matchIdx)}).sort('cheer_datetime', -1))
    for content in contents:
        content["_id"] = str(content["_id"])

    # print(matchIdx)

    #
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        return render_template('cheer.html', match=match, contents=contents, user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 글 작성
@app.route("/api/set_cheer", methods=['POST'])
def set_cheer():
    userId = request.form['userId']
    nickName = request.form['nickName']
    matchIdx = request.form['matchIdx']
    cheer_team = request.form['cheerTeam']
    cheer_content = request.form['content']
    now = datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

    doc = {
        'user_id': userId,
        'nick_name': nickName,
        'match_idx': ObjectId(matchIdx),
        'cheer_team': cheer_team,
        'cheer_content': cheer_content,
        'cheer_datetime': nowDatetime
    }

    db.contents.insert_one(doc)
    return jsonify({'msg': '저장완료'})


# 경기 삭제
@app.route("/delMatch/<matchIdx>", methods=['GET'])
def del_match(matchIdx):
    # matchIdx = request.form['matchIdx']
    # print(matchIdx)
    matches = list(db.matches.find().sort('cheer_datetime', -1))

    for match in matches:
        match["_id"] = str(match["_id"])

    db.matches.delete_one({'_id': ObjectId(matchIdx)})
    # return render_template('index.html')

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})

        return render_template('index.html', matches=matches, user_info=user_info)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 글 삭제
@app.route("/delContent/<contentIdx>", methods=['GET'])
def del_content(contentIdx):
    db.contents.delete_one({'_id': ObjectId(contentIdx)})
    return jsonify('msg')


# 회원 삭제
@app.route("/delUser/<userIdx>", methods=['GET'])
def del_user(userIdx):
    db.users.delete_one({'_id': ObjectId(userIdx)})
    return jsonify('msg')



# 관리자 - 회원 비활성화/활성화
@app.route("/updateUser/<userIdx>", methods=['GET'])
def update_user(userIdx):
    target_user = db.users.find_one({"_id": ObjectId(userIdx)})
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})

        if target_user['grade'] == 0:
            db.users.update_one({"_id": ObjectId(userIdx)}, {'$set': {"grade": -1}})
        elif target_user['grade'] == -1:
            db.users.update_one({"_id": ObjectId(userIdx)}, {'$set': {"grade": 0}})
        users = list(db.users.find().sort('join_date', -1))

        return render_template('adminUser.html', user_info=user_info, users=users)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



# 관리자 페이지
@app.route("/admin/<manageType>", methods=['GET'])
def admin(manageType):
    # return render_template('adminSchedule.html')
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        if manageType == 'schedule':
            return render_template('adminSchedule.html', user_info=user_info)
        elif manageType == 'contents':
            contents = list(db.contents.find().sort('cheer_datetime', -1))
            return render_template('adminContents.html', user_info=user_info, contents=contents)
        elif manageType == 'user':
            users = list(db.users.find().sort('join_date', -1))
            return render_template('adminUser.html', user_info=user_info, users=users)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 경기 등록
@app.route("/api/set_match", methods=['POST'])
def set_match():
    home_team = request.form['homeTeam']
    away_team = request.form['awayTeam']
    match_day = request.form['matchDay']
    stadium = request.form['stadium']

    doc = {
        'home_team': home_team,
        'away_team': away_team,
        'match_day': match_day,
        'stadium': stadium
    }
    db.matches.insert_one(doc)
    return jsonify({'msg': '저장완료'}, )

@app.route("/mypage/<userIdx>", methods=['GET'])
def mypage(userIdx):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"user_id": payload["id"]})
        contents = list(db.contents.find({"user_id": ObjectId(userIdx)}).sort('cheer_datetime', -1))
        return render_template('mypage.html', contents=contents, user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
