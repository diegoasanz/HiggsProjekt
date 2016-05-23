# utility functions

from ROOT import gROOT, TCanvas
import ROOT
from datetime import datetime
from termcolor import colored

def log_warning(msg):
    t = datetime.now().strftime('%H:%M:%S')
    print '{head} {t} --> {msg}'.format(t=t, msg=msg, head=colored('WARNING:', 'red'))

def print_banner(msg, symbol='='):
    print '\n{delim}\n{msg}\n{delim}\n'.format(delim=len(str(msg)) * symbol, msg=msg)

def format_histo(histo, name='', title='', x_tit='', y_tit='', z_tit='', marker=20, color=1, markersize=1, x_off=1, y_off=1, z_off=1, lw=1, fill_color=0):
        h = histo
        h.SetTitle(title) if title else h.SetTitle(h.GetTitle())
        h.SetName(name) if name else h.SetName(h.GetName())
        try:
            h.SetMarkerStyle(marker)
            h.SetMarkerColor(color) if color is not None else h.SetMarkerColor(h.GetMarkerColor())
            h.SetLineColor(color) if color is not None else h.SetLineColor(h.GetLineColor())
            h.SetMarkerSize(markersize)
            h.SetFillColor(fill_color)
            h.SetLineWidth(lw)
            h.GetXaxis().SetTitle(x_tit) if x_tit else h.GetXaxis().GetTitle()
            h.GetXaxis().SetTitleOffset(x_off)
            h.GetYaxis().SetTitle(y_tit) if y_tit else h.GetYaxis().GetTitle()
            h.GetYaxis().SetTitleOffset(y_off)
            h.GetZaxis().SetTitle(z_tit) if z_tit else h.GetZaxis().GetTitle()
            h.GetZaxis().SetTitleOffset(z_off)
        except AttributeError or ReferenceError:
            pass

def save_plots(savename, save_dir, file_type=None,  sub_dir=None, canvas=None):
        save_dir = save_dir
        file_type = '.png' if file_type is None else '.{end}'.format(end=file_type)
        sub_dir = '' if sub_dir is None else '{subdir}/'.format(subdir=sub_dir)
        resultsdir = save_dir + sub_dir
        if canvas is None:
            try:
                c = gROOT.GetListOfCanvases()
                canvas = c[-1]
            except Exception as inst:
                print_banner('ERROR in get canvas! {inst}'.format(inst=inst))
                return
        canvas.Update()
        try:
            canvas.SaveAs(resultsdir + savename + file_type)
        except Exception as inst:
            print_banner('ERROR in save plots! {inst}'.format(inst=inst))

def draw_histo(histo, save_name, show, save_dir, lm=.1, rm=0.1, draw_opt='', x=2000, y=2000, l=None):
        h = histo
        gROOT.SetBatch(1) if not show else do_nothing()
        c = TCanvas('c_{0}'.format(h.GetName()), h.GetTitle().split(';')[0], x, y)
        c.SetMargin(lm, rm, .15, .1)
        h.Draw(draw_opt)
        l.Draw() if l is not None else do_nothing()
        save_plots(save_name, save_dir)
        gROOT.SetBatch(0)
        return [c, h, l] if l is not None else [c, h]


def create_colorlist():
    col_names = [ROOT.kGreen, ROOT.kOrange, ROOT.kViolet, ROOT.kYellow, ROOT.kRed, ROOT.kBlue, ROOT.kMagenta, ROOT.kAzure, ROOT.kCyan, ROOT.kTeal]
    colors = []
    for color in col_names:
        colors.append(color + 1)
    for color in col_names:
        colors.append(color + 3)
    return colors

colorlist = create_colorlist()
count = 0

def get_color():
    global count
    count %= 20
    color = colorlist[count]
    count += 1
    return color

def do_nothing():
    pass