import json
import os
import sqlite3

from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from cfg import cfg
from common.logger import Logger
from svc import svc

# --------------------
## Create a Flask application instance.
#  * the application's module or package.
#  * the location of the template folder
template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_folder)


# --------------------
## holds common info for
class Info:
    ## holds ping count
    ping_count = 0
    ## indicate if an entry was deleted
    entry_deleted = False
    ## holds path to database
    db_path = os.path.join('webhost', 'notify_server.db')

    # --------------------
    ## initialize
    # @return None
    @classmethod
    def init(cls):
        cfg.load()
        cls.ping_count = 0
        cls.entry_deleted = False


# --------------------
## generate a notification table
#
# @return HTML for the table
def _gen_notification_table():
    px_ch = 9
    headers = [
        ('del_btn', ' ', px_ch * 8, 'center'),  # delete button
        ('dts', 'date', px_ch * 19, 'center'),  # DTS received (or sent?)
        ('source', 'source', px_ch * 12, 'center'),  # hostname that sent the notification
        ('tag', 'event', px_ch * 22, 'center'),  # notification name
        ('status', 'status', px_ch * 7, 'center'),  # ok, err, warn
        ('desc', 'description', None, 'left'),  # (optional) additional description of what happened
        # 'data   - (optional) additional data to store
    ]

    conn = sqlite3.connect(Info.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notifications')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()

    notify_table = ''
    notify_table += '<table>\n'
    notify_table += '<tr>\n'
    for header in headers:
        # handle del btn
        if header[2]:
            style = 'style="'
            style += f'width:{header[2]}px;text-align:{header[3]};'
            style += '"'
        else:
            style = ''
        notify_table += f'  <th {style}>{header[1]}</th>\n'
    notify_table += '</tr>\n'

    for row in rows:
        notify_table += '<tr>\n'

        id_tag = row[0]
        data = json.loads(row[1])
        # svc.log.dbg(f'{row[0]}] data: {data}')
        for _, hdr_info in enumerate(headers):
            style = f'style="text-align:{hdr_info[3]};"'
            if hdr_info[0] == 'del_btn':
                #                 id_tag = '{{ id }}'
                notify_table += '<td>\n'
                notify_table += f' <form {style} method="post" action="/delete_notify/{id_tag}">\n'
                notify_table += '   <button type="submit">Delete</button>\n'
                notify_table += ' </form>\n'
                notify_table += '</td>\n'
                continue

            val = data.get(hdr_info[0])
            notify_table += f'<td {style}>{val}</td>\n'
        notify_table += '</tr>\n'

    notify_table += '</table>\n'

    return notify_table


# --------------------
## Define a route for default path. Uses index.html template
#
# @return rendered html for index page
@app.route('/')
def index():
    title = 'Notifier'

    entry_deleted = Info.entry_deleted
    Info.entry_deleted = False

    notify_table = _gen_notification_table()
    return render_template('index.html',
                           title=title, pings=Info.ping_count, notify_table=notify_table, entry_deleted=entry_deleted)


# --------------------
## Define a route for ping POST.
#
# @return 200 response
@app.route('/ping', methods=['POST'])
def ping():
    Info.ping_count += 1

    # uncomment to debug
    # data = request.get_json()  # if you're sending JSON data
    # svc.log.dbg(f'recv ping  : data={data}')

    # TODO check how to auto-refresh screen?
    # Process the data here
    # result = {'message': 'POST request received', 'data': data}
    # svc.log.dbg(result)

    return make_response('ping successful', 200)


# --------------------
## Define a route for notification POST.
#
# @return 200 response
@app.route('/notify', methods=['POST'])
def notify():
    # if you're sending JSON data
    data = request.get_json()
    # svc.log.dbg(f'recv notify: data={data}')

    data_str = json.dumps(data)
    conn = sqlite3.connect(Info.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notifications (data) VALUES (?)
    """, (data_str,))
    conn.commit()
    conn.close()

    return make_response('notify successful', 200)


# --------------------
## Define a route to delete a notification entry with the given id
#
# @return rendered html for index page
@app.route('/delete_notify/<int:id_tag>', methods=['POST'])
def notify_delete(id_tag):
    svc.log.dbg(f'delete {id_tag}')

    conn = sqlite3.connect(Info.db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM notifications WHERE id = ?
        """,
        (id_tag,),
    )
    conn.commit()

    # redirect to index.html
    Info.entry_deleted = True
    return redirect(url_for('index'))


# --------------------
## mainline
def main():
    svc.log = Logger()

    Info.init()

    conn = sqlite3.connect(Info.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            data JSON
        )
    """)
    conn.commit()
    conn.close()

    # only run at start up time; note that script is auto restarted by flask when debug=True
    svc.log.start(f'server.main host={cfg.server_ip}, port={cfg.server_port}, debug={cfg.is_debug}')
    app.run(host=cfg.server_ip, port=cfg.server_port, debug=cfg.is_debug)


# This is a special idiom in Python that means:
# "If this script is being run directly (not imported as a module),
#  then execute the following code.
if __name__ == '__main__':
    main()
