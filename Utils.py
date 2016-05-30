# utility functions

from ROOT import gROOT, TCanvas, TGraphErrors, TLegend
import ROOT
from datetime import datetime
from termcolor import colored


def log_warning(msg):
    t = datetime.now().strftime('%H:%M:%S')
    print '{head} {t} --> {msg}'.format(t=t, msg=msg, head=colored('WARNING:', 'red'))


def print_banner(msg, symbol='='):
    print '\n{delim}\n{msg}\n{delim}\n'.format(delim=len(str(msg)) * symbol, msg=msg)


def format_histo(histo, name='', title='', x_tit='', y_tit='', z_tit='', marker=20, color=1, markersize=1, x_off=1, y_off=1, z_off=1, lw=1, fill_color=0, stats=True):
        h = histo
        h.SetTitle(title) if title else h.SetTitle(h.GetTitle())
        h.SetName(name) if name else h.SetName(h.GetName())
        try:
            h.SetStats(0) if not stats else do_nothing()
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


def save_histo(histo, save_name, show, save_dir, lm=.1, rm=0.1, draw_opt='', x=2000, y=2000, l=None, logy=False):
        gROOT.ProcessLine('gErrorIgnoreLevel = kError;')
        h = histo
        gROOT.SetBatch(1) if not show else gROOT.SetBatch(0)
        c = TCanvas('c_{0}'.format(h.GetName()), h.GetTitle().split(';')[0], x, y)
        c.SetLogy() if logy else do_nothing()
        c.SetMargin(lm, rm, .1, .1)
        h.Draw(draw_opt)
        l.Draw() if l is not None else do_nothing()
        save_plots(save_name, save_dir)
        gROOT.SetBatch(0)
        gROOT.ProcessLine('gErrorIgnoreLevel = 0;')
        return [c, h, l] if l is not None else [c, h]


def make_legend(x1=.6, y2=.9, nentries=2, w=.3, scale=1, felix=False):
    x2 = x1 + w
    y1 = y2 - nentries * .05 * scale
    l = TLegend(x1, y1, x2, y2)
    l.SetName('l')
    l.SetTextFont(42)
    l.SetTextSize(0.03 * scale)
    if felix:
        l.SetLineWidth(2)
        l.SetBorderSize(0)
        l.SetFillColor(0)
        l.SetFillStyle(0)
        l.SetTextAlign(12)
    return l


def make_tgrapherrors(name, title, color=1, marker=20, marker_size=1, width=1):
    gr = TGraphErrors()
    gr.SetTitle(title)
    gr.SetName(name)
    gr.SetMarkerStyle(marker)
    gr.SetMarkerColor(color)
    gr.SetLineColor(color)
    gr.SetMarkerSize(marker_size)
    gr.SetLineWidth(width)
    return gr


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

BranchDict = {'mvis': 'Visible Mass', 'mmis': 'Missing Mass'}
