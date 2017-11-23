"""
BlogCalendar provides html calendar for Django model containing
the date field. If model items do exist for the particular date,
BlogCalendar adds html link to the date-based url.


Example:

    # args
    model = Post                      # django model with DateField or DateTimeField
    date_field = 'created'            # DateField or DateTimeField name in model
    url_name = 'simpleblog:calendar'  # url name for links
                                      # url should have <year> <month> and <day> parameters

    # kwargs:
    additional_filters = {'is_public':True}  # additional filtering instructions
                                             # default is None

    day_abbr = ['Mo','Tu','We','Th','Fr','Sa','Su'] # days of week abbreviations
                                                    # default is calendar.day_abbr

    b = BlogCalendar(model,
                    date_field,
                    url_name,
                    additional_filters=additional_filters,
                    day_abbreviations=day_abbr)

    # html calendar for current month
    current_date = date.today()
    print (b.formatmonth(current_date.year, current_date.month))

    # html calendar for current year
    print (b.formatyear(current_date.year))

"""

__author__ = "blacktower2016"
__date__ = "21.11.2017"
__license__ = "MIT"

from django.urls import reverse
from django.db.models import Q
from calendar import HTMLCalendar, day_abbr
from datetime import date


class BlogCalendar(HTMLCalendar):
    """
    BlogCalendar provides html calendar for Django model containing
    the date field. If model items do exist for the particular date,
    BlogCalendar adds html link to the date-based url.

    args:
        model:          # django model with DateField or DateTimeField
        date_field:     # DateField or DateTimeField name in model
        url_name:       # url name for links
                        # url should have <year> <month> and <day> parameters
    kwargs:
        additional_filters (dict, optional): # additional filtering instructions
                                             # default is None

        day_abbreviations (iterable with 7 day names as strings, optional):
                                            # days of week abbreviations
                                            # default is calendar.day_abbr
    """

    def __init__(self, model, date_field, url_name, additional_filters=None, day_abbreviations=None):
        self.model = model
        self.date_field = date_field
        self.url_name = url_name
        self.additional_filters = additional_filters
        self.day_abbr = day_abbreviations or day_abbr
        super().__init__()

    def formatday(self, day, weekday, monthyear=None):
        """
        Return day as a table data <td> with links to url_name
        """
        themonth, theyear = monthyear
        inner ='{}'
        classes = self.cssclasses[weekday]

        if day!=0:
            if date.today() == date(theyear, themonth, day):
                classes+=' today'
                inner = '<span>{}</span>'

            lookup_date = '{}__date'.format(self.date_field)
            query_filter = Q(**{lookup_date:date(theyear, themonth, day)})
            if self.additional_filters:
                query_filter = query_filter & Q(**self.additional_filters)

            if self.model._default_manager.filter(query_filter):
                inner = '<a href="'+reverse(self.url_name, kwargs={'year':theyear, 'month':themonth, 'day':day })+'">{}</a>'

            return '<td class="{}">{}</td>'.format(classes, inner.format(day))

        return '<td class="noday">&nbsp;</td>' # day outside month


    def formatweek(self, theweek, monthyear=None):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, monthyear) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s">%s</th>' % (self.cssclasses[day], self.day_abbr[day])

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        monthyear = (themonth, theyear)
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, monthyear))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
