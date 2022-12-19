import streamlit as st
import pandas as pd
import base64
import hashlib
import hmac
import base64
import datetime
import requests
import json
import time as t



# DB Managment
import sqlite3

conn_log = sqlite3.connect('data.db')
c = conn_log.cursor()

#conn = sqlite3.connect('Jdream_url.db')
#c_jd = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username,password))
    conn_log.commit()

def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username,password))
    data = c.fetchall()
    return data

def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data

def file_downloader(filename, file_label='File'):
    with open(filename, 'rb') as f:
        data = f.read()

def JDream_api_response(name, id, secretKey):
    dt_now = datetime.datetime.now()
    time = dt_now.strftime('%Y%m%d%H%M%S')


    signature = hmac.new(key=bytes(secretKey,'utf-8'), msg=bytes(id+':'+time,'utf-8'), digestmod=hashlib.sha256).digest()
    base64_signature = base64.b64encode(signature).decode()

    url = "https://expert.jdream3.com/app/external_api/supply/auth/info"
    payload = {
        "user_id":id, 
        "token":base64_signature, 
        "time":time,
        "authors":[{"name" : name}]
        }
    headers = {'Content-type':"application/json"}

    t.sleep(1)
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    return r

def main():
    """ Simple Login App """

    st.title("Excel for FileMaker データ更新APP")


    #menu  = ["Home","Login","SignUp"]
    menu = ['Update']
    choice = st.sidebar.selectbox("Menu", menu)

    #JD_data_df = pd.read_sql_query('SELECT * FROM Jdream_url', conn)
    #submit_btn_DB = st.button('DBのカラム')

    #ボタンが押されたら処理を実行する
    #if submit_btn_DB:
        #st.table(JD_data_df.columns)

    if choice == "Update":
        #st.subheader("")
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            create_usertable()
            result = login_user(username, password)
            if result:
                st.success("Logged In as {}".format(username))


                task = st.selectbox("Please Select Task", ["Update DB"])
                if task == "Add Post":
                    st.subheader("Add Your Post")

                elif task == "Analytics":
                    st.subheader("Analytics")

                elif task == "Profiles":
                    st.subheader("Profiles")
                    user_result = view_all_users()
                    clean_db = pd.DataFrame(user_result, columns=["username","Password"])
                    st.dataframe(clean_db)

                elif task == "Update DB":
                    id = st.text_input('JDreamIDを入力', '')
                    secretKey = st.text_input('APIキーを入力','')
                    old_uploaded_excel = st.file_uploader('古いファイルをアップロード', type='xlsx')
                    new_uploaded_excel = st.file_uploader('新しいファイルをアップロード', type='xlsx')
                    submit_btn_xlsx = st.button('処理実行')
                    #ボタンが押されたら処理を実行する
                    if submit_btn_xlsx:
                        #st.write(pd.read_excel(uploaded_excel))
                        old_df = pd.read_excel(old_uploaded_excel)
                        #old_df = old_df[['職員番号','氏名','名前カナ','部局名','職名','リンクコピー']]
                        new_df = pd.read_excel(new_uploaded_excel)

                        new_researcher_df = new_df[~(new_df['職員番号'].isin(old_df['職員番号'].unique()))]

                        #JDのAPIでリンクを作成
                        JDream_url = 'https://expert.jdream3.com/app/author/detail/'
                        JDream_user_url_list = []

                        for name in new_researcher_df['氏名']:
                            #API接続
                            try:
                                r = JDream_api_response(name, str(id), str(secretKey))
                                st.write(r)
                                author_id = json.loads(r.text)['data'][0]['authorId']
                                organization = json.loads(r.text)['data'][0]['organization']
                                if organization == '北海道大学':
                                #JDream接続リンクを作成
                                    JDream_user_url = JDream_url + author_id
                                else:
                                    JDream_user_url = ''
                            except:
                                JDream_user_url = ''
                            
                            JDream_user_url_list.append(JDream_user_url)
                            st.write(JDream_user_url)

                        new_researcher_df['リンクコピー'] = JDream_user_url_list

                        st.write('追加される研究者')
                        st.dataframe(new_researcher_df)

                        
                        csv = new_researcher_df.to_csv(index=False)
                        #st.table(csv_file)
                        #csv = df.to_csv(index=False) 
                        b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="result_utf-8-sig.csv">CSVファイルをダウンロード</a>'
                        #st.markdown(f"CSVファイルのダウンロードはこちら:  {href}", unsafe_allow_html=True)
                        st.markdown(f"{href}", unsafe_allow_html=True)

                    
            else:
                st.warning("Incorrect Username/Password")


        



    # elif choice == "Login":
    #     st.subheader("Login Section")

    #     username = st.sidebar.text_input("User Name")
    #     password = st.sidebar.text_input("Password", type='password')
    #     if st.sidebar.checkbox("Login"):
    #         #if password == '12345':
    #         create_usertable()
    #         result = login_user(username, password)
    #         if result:
    #             st.success("Logged In as {}".format(username))

    #             task = st.selectbox("Task", ["Add Post", "Analytics","Profiles"])
    #             if task == "Add Post":
    #                 st.subheader("Add Your Post")

    #             elif task == "Analytics":
    #                 st.subheader("Analytics")

    #             elif task == "Profiles":
    #                 st.subheader("Profiles")
    #                 user_result = view_all_users()
    #                 clean_db = pd.DataFrame(user_result, columns=["username","Password"])
    #                 st.dataframe(clean_db)
    #         else:
    #             st.warning("Incorrect Username/Password")


    # elif choice == "SignUp":
    #     st.subheader("Create New Account")
    #     new_user = st.text_input("Username")
    #     new_password = st.text_input("Password", type='password')

    #     if st.button("Signup"):
    #         create_usertable()
    #         add_userdata(new_user, new_password)

    #         st.success("You have successfully created a valid Account")
    #         st.info("Go to Login Menu to login")


if __name__ == '__main__':
    main()

