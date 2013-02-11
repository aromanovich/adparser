Парсер объявлений об аренде (написан в помощь администраторам http://vk.com/ekb_arenda).  
Пробегает по списку URL-ов объявлений и добавляет к ним краткое описание в формате, принятом в сообществе.

Например:
```
http://www.e1.ru/business/realty/4504836.html
http://www.e1.ru/business/realty/4502779.html
http://www.e1.ru/business/realty/4500268.html
http://www.e1.ru/business/realty/4504685.html
```
&rarr;
```
http://www.e1.ru/business/realty/4504836.html — 1кв, 20000 (ку включены), Пехотинцев 3/4 (Н.Сортировка)
http://www.e1.ru/business/realty/4502779.html — 1кв, 17000+ку, Татищева 53 (ВИЗ)
http://www.e1.ru/business/realty/4500268.html — 1кв, 16000 (ку включены), Дизельный (Чермет)
http://www.e1.ru/business/realty/4504685.html — 1кв, 16000 (ку включены), Шварца 18/1 (Ботанический)
```

Парсер хостится на [Heroku](http://www.heroku.com/) и доступен по адресу http://adparser.aromanovich.ru/.
