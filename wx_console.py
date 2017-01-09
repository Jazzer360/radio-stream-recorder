import logging
import wx

import wx.lib.newevent

# create event type
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()


class wxLogHandler(logging.Handler):
    def __init__(self, wxDest=None):
        logging.Handler.__init__(self)
        self.wxDest = wxDest
        # self.level = logging.DEBUG

    def emit(self, record):
        try:
            msg = self.format(record)
            evt = wxLogEvent(msg=msg)
            wx.PostEvent(self.wxDest, evt)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class TaskbarIcon(wx.TaskBarIcon):
    def __init__(self, frame, icon, title):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(icon), title)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)

    def OnTaskBarClose(self, evt):
        self.frame.Close()

    def OnTaskBarLeftClick(self, evt):
        self.frame.Show()
        self.frame.Restore()


class LoggingFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        icon = kwargs.pop('icon')
        super(LoggingFrame, self).__init__(*args, **kwargs)

        self.handler = wxLogHandler(self)

        self.Bind(wx.EVT_ICONIZE, self.onMinimize)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(EVT_WX_LOG_EVENT, self.onLog)

        self.tb_icon = TaskbarIcon(self, icon, kwargs['title'])

        panel = wx.Panel(self, wx.ID_ANY)
        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        self.console = wx.TextCtrl(panel, wx.ID_ANY, size=(300, 100),
                                   style=style)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.console, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)

    def onClose(self, evt):
        self.tb_icon.RemoveIcon()
        self.tb_icon.Destroy()
        self.Destroy()

    def onMinimize(self, event):
        if self.IsIconized():
            self.Hide()

    def onLog(self, e):
        self.console.AppendText('%s\n' % e.msg)
        self.console.ScrollLines(-1)


# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = LoggingFrame(None, title="test", icon="record.png").Show()
    app.MainLoop()
