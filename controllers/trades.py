@auth.requires_login()
def index():
    trades = db((db.trades.UserProposing == auth.user.id) & (auth.user.id == db.auth_user.id)).select()
    if len(trades)>0:
        return dict(trades = trades)
    else:
        return dict()