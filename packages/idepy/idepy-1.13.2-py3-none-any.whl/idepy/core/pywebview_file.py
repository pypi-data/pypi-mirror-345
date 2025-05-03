import webview


def select_folder_path(**kwargs):
    """
    选择文件夹路径
    :param kwargs:
    :return:
    """
    from idepy.core.main import get_app
    app = get_app()
    w: webview.Window = app.main_window
    kwgs = {
        "dialog_type": webview.FOLDER_DIALOG,
        **kwargs
    }
    p = w.create_file_dialog(**kwgs)
    if p:
       return p[0]
    return None


def select_file_path(**kwargs):
    """
    选择文件地址
    :param kwargs:
    :return:
    """
    from idepy.core.main import get_app
    app = get_app()
    w: webview.Window = app.main_window
    kwgs = {
        "dialog_type": webview.OPEN_DIALOG,
        **kwargs
    }
    p = w.create_file_dialog(**kwgs)
    if p:
       return p[0]
    return None


def select_file_save_path(**kwargs):
    """
    选择文件保存地址
    :param kwargs:
    :return:
    """
    from idepy.core.main import get_app
    app = get_app()
    w: webview.Window = app.main_window
    kwgs = {
        "dialog_type": webview.SAVE_DIALOG,
        **kwargs
    }
    p = w.create_file_dialog(**kwgs)
    if p:
       return p[0]
    return None

def select_folder_save_path(**kwargs):
    """
    选择文件夹保存地址
    :param kwargs:
    :return:
    """
    from idepy.core.main import get_app
    app = get_app()
    w: webview.Window = app.main_window
    kwgs = {
        "dialog_type": webview.FOLDER_DIALOG,
        **kwargs
    }
    p = w.create_file_dialog(**kwgs)
    if p:
       return p[0]
    return None
