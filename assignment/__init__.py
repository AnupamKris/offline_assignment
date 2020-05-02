from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uoasf78c23ybr78w87ayer782nvtcrj1ho3ntadfsf'

from assignment import routes