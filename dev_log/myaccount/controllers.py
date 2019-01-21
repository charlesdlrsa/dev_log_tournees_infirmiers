from flask import Blueprint, request, render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import re
from sqlalchemy.sql import or_
from dev_log import db
from dev_log.models import Absence
from dev_log.auth.controllers import login_required

account = Blueprint('account', __name__, url_prefix='/account')


@account.route('/edit', methods=['GET', 'POST'])
@login_required
def home():
    return render_template('account.html')


@account.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_account(id):
    if session['user_type'] == 'nurse':
    # edit nurse ?
    elif session['user_type'] == 'admin':



# edit admin


@account.route('/absence', methods=['GET', 'POST'])
@login_required
def absence():
