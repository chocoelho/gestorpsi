# -*- coding: utf-8 -*-

"""
    Copyright (C) 2008 GestorPsi
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from dateutil.relativedelta import relativedelta

from gestorpsi.gcm.models.payment import PaymentType
from gestorpsi.gcm.models.plan import Plan


INVOICE_STATUS_CHOICES = (
    (0, _(u'Pendente')),
    (1, _(u'Pago pelo Cliente')),
    (2, _(u'Pago / 1 mês grátis')),
)

INVOICE_TYPES = (
    ('1', _('Inscription')),
    ('2', _('Monthly fee')),
)

PAYMENT_WAY = (
    ('1', _(u'Boleto')),
    ('2', _(u'Cartão crédito')),
)

BANK = (
    ('1', _(u'PagSeguro cartão crédito')),
    ('2', _(u'PagSeguro boleto')),
    ('99', _(u'Depósito em conta')),
)


class Invoice(models.Model):
    type = models.CharField(max_length=2, null=False, blank=False, choices=INVOICE_TYPES, default='2')
    
    organization = models.ForeignKey('organization.Organization', verbose_name=_('Organizacao'))
    date = models.DateTimeField(_('Data'), auto_now_add=True) # data que foi gerado
    
    date_payed = models.DateField(_(u'Data do Pagamento'), null=True, blank=True)
    date_payed.help_text=_('Preencher apenas quando efetuado pagamento. Formato aaaa/mm/dd Ex: 2014-12-31')
    
    start_date = models.DateField(_(u'Data início periodo'), null=False, blank=False)
    start_date.help_text=_('Formato aaaa/mm/dd Ex: 2014-12-31')

    end_date = models.DateField(_(u'Data do fim Periodo'), null=False, blank=False)
    end_date.help_text=_('Formato aaaa/mm/dd Ex: 2014-12-31')
    
    expiry_date = models.DateField(_('Data de Expiracao'), null=True, blank=True)
    expiry_date.help_text = _('Formato aaaa/mm/dd  Ex: 2014-12-31 Data em que o plano vence. Conta do cliente modo apenas leitura.')
    
    ammount = models.DecimalField(_('Valor'), decimal_places=2, max_digits=8, null=True, blank=True)
    ammount.help_text=_('Utilizar pontos, nao virgulas. Ex.: 39.90')
    
    discount = models.DecimalField(_('Desconto'), decimal_places=2, max_digits=8, null=True, blank=True)
    discount.help_text=_('Valor para desconto. Utilizar apenas valores decimais aqui, NAO porcentagem. Ex.: 5.90')
    
    payment_type = models.ForeignKey(PaymentType, null=False, blank=False, related_name='payment_type', verbose_name='Forma de pagamento') # from org choosen

    status = models.IntegerField(_(u'Situação'), choices=INVOICE_STATUS_CHOICES, default=0)
    plan = models.ForeignKey(Plan, verbose_name=_('Plan'), null=True, blank=True)

    bank = models.CharField(_('Banco'), choices=BANK, max_length=3, null=True, blank=True)
    payment_detail = models.TextField(_(u'Detalhes do pagamento'), null=True, blank=True)
    
    class Meta:
        app_label = 'gcm'
        ordering = ['organization', '-date', ]
    
    def __unicode__(self):
        return u'%s - %s %s' % (self.organization, self.date.strftime('%d/%m/%Y'), self.plan)
    
    #def dued(self):
        #return self.due_date < datetime.today()
            
    
    def save(self, *args, **kargs):

        # new
        if not self.id:
            self.date = datetime.now()
            self.ammount = self.organization.prefered_plan.value
            self.plan = self.organization.prefered_plan

        # gratis / register
        if self.status == 2:
            self.date_payed = datetime.today()
            self.start_date = self.date_payed
            self.end_date = self.start_date + relativedelta(months=1)
            self.expiry_date = self.end_date

        super(Invoice, self).save()
