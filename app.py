# encoding: utf-8
import re
from urlparse import urlparse

import requests
from lxml.html import document_fromstring
from cssselect import GenericTranslator
from flask import Flask, render_template, request


app = Flask(__name__)


def q(document, css3_selector, immediate=False):
    expression = GenericTranslator().css_to_xpath(css3_selector)

    text = None
    if immediate:
        result = document.xpath(expression + '/text()')
        if result:
            text = ' '.join(result)
    else:
        result = document.xpath(expression)
        if result:
            text = result[0].text_content()

    return text and ' '.join(text.split())


def parse_e1(document):
    data = {}

    title = q(document,
              'table[cellspacing="1"][cellpadding="3"]>'
              'tbody>tr>td[bgcolor="#bababa"]')
    if title:
        match = re.match(ur'(?P<rooms>\d) комнатная квартира, сдам', title)
        if match:
            data['type'] = 'flat'
            data['rooms'] = int(match.group('rooms'))
        elif title.startswith(u'Комната'):
            data['type'] = 'room'

    price = q(document, u'td:contains("Цена")+td>b')
    if price:
        data['price'] = int(price.replace(' ', '').strip(u'р'))

    payments = q(document, u'td:contains("Коммунальные платежи")+td')
    if payments:
        assert payments in (u'Включены в стоимость',
                            u'Оплачиваются дополнительно')
        data['payments_included'] = payments == u'Включены в стоимость'

    data['district'] = q(document, u'td:contains("Район")+td')

    data['address'] = q(document, u'td:contains("Адрес")+td>b', immediate=True)

    return data


def parse_avito(document):
    data = {}

    title = q(document, 'h1.item_title.item_title-large')
    match = re.search(ur'^(?P<rooms>\d)-к квартира', title)
    if match:
        data['type'] = 'flat'
        data['rooms'] = int(match.group('rooms'))
    elif title.startswith(u'Комната'):
        data['type'] = 'room'

    price = q(document, u'span.p_i_price')
    if price:
        match = re.search('^(?P<price>\d+)', price.replace(' ', ''))
        if match:
            data['price'] = int(match.group('price'))

    address = q(document, u'dt:contains("Адрес")+dd', immediate=True)
    data['address'] = address.strip().strip(' ,')

    return data


def parse_slando(document):
    data = {}

    title = q(document, u'div:contains("Тип аренды:")>strong>a')
    rooms = q(document, u'div:contains("Всего комнат в квартире:")>strong') or \
        q(document, u'div:contains("Количество комнат:")>strong')

    if title and rooms:
        if title == u'Долгосрочная аренда квартир':
            data['type'] = 'flat'
            data['rooms'] = int(rooms)
        elif title == u'Долгосрочная аренда комнат':
            data['type'] = 'room'

    price = q(document, u'.pricelabel *:contains("руб.")')
    if price:
        match = re.search('^(?P<price>\d+)', price.replace(' ', ''))
        if match:
            data['price'] = int(match.group('price'))

    address = q(document, u'.locationbox p:contains("Адрес:")+p')
    if address:
        city_prefix = u'Екатеринбург, '
        if address.startswith(city_prefix):
            address = address[len(city_prefix):]
        data['address'] = address

    return data


def to_summary(data):
    result = u''

    type_ = data.get('type')
    if type_ == 'flat':
        result += u'%sкв' % data['rooms']
    elif type_ == 'room':
        result += u'комната'

    price = data.get('price')
    if price:
        result += ', %i' % price

    payments_included = data.get('payments_included')
    if payments_included is not None:
        if payments_included:
            result += u' (ку включены)'
        else:
            result += u'+ку'

    address = data.get('address')
    if address:
        result += ', %s' % address

    district = data.get('district')
    if district is not None:
        result += ' (%s)' % district

    return result


supported_sites = {
    'e1.ru': (parse_e1, 'cp1251'),
    'avito.ru': (parse_avito, 'utf8'),
    'slando.ru': (parse_slando, 'utf8'),
}


def parse_ad(url):
    domain = urlparse(url).netloc
    for site, (parse, encoding) in supported_sites.iteritems():
        if site not in domain:
            continue
        response = requests.get(url)
        content = unicode(response.content, encoding)
        document = document_fromstring(content)
        try:
            data = parse(document)
            return to_summary(data)
        except:
            pass


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    context = {}

    input_ = request.form.get('urls')
    if request.method == 'POST' and input_:
        urls = map(unicode.strip, input_.split('\n'))
        context['result'] = zip(urls, map(parse_ad, urls))

    return render_template('main.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
