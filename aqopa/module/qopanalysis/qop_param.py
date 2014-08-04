#!/usr/bin/env python

"""
@file       qop_param.py
@brief      a class that describes a single QoP paramater
@author     Katarzyna Mazur
"""

class QoPParameter():

    # static params counter
    qop_param_num = 1

    def __init__(self, qop_param_name="", fun_name="", val=""):
        # those values can describe the QoP parameters
        self.qop_label = "qopanalysis" + QoPParameter.qop_param_num
        self.qop_param_name = qop_param_name
        self.fun_name = fun_name
        self.val = val

        QoPParameter.qop_param_num += 1

    def __str__(self):
        return "QoP[label=%s, name=%s, function=%s, value=%s]" % (self.qop_label, self.qop_param_name, self.fun_name, self.val)

    def __repr__(self):
        return "QoP[label=%s, name=%s, function=%s, value=%s]" % (self.qop_label, self.qop_param_name, self.fun_name, self.val)

    def __unicode__(self):
        return u"QoP[label=%s, name=%s, function=%s, value=%s]" % (self.qop_label, self.qop_param_name, self.fun_name, self.val)