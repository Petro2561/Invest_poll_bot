from datetime import date, datetime
from typing import Dict
from zoneinfo import ZoneInfo


from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import (Calendar,
                                                     CalendarDaysView,
                                                     CalendarMonthView,
                                                     CalendarScopeView,
                                                     CalendarYearsView,
                                                     CalendarUserConfig,
                                                     get_today,
                                                     DATE_TEXT,
                                                     TODAY_TEXT
)
from aiogram_dialog.widgets.text import Format, Text
from aiogram_dialog.api.internal import RawKeyboard


SELECTED_DAYS_KEY = "selected_dates"


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: datetime.date = data["date"]
        return ("пн", "вт", "ср", "чт", "пт", "сб", "вс")[selected_date.weekday()]
    
class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        if serial_date in selected:
            return self.mark
        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: datetime.date = data["date"]
        return (
            "январь",
            "февраль",
            "март",
            "апрель",
            "май",
            "июнь",
            "июль",
            "август",
            "сентябрь",
            "октябрь",
            "ноябрь",
            "декабрь",
        )[selected_date.month - 1]


class RuCalendar(Calendar):
    def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                date_text=MarkedDay("🎾", DATE_TEXT),
                today_text=MarkedDay("🎾", TODAY_TEXT),
                weekday_text=WeekDay(),
                header_text=Month() + Format("{date: %Y}"),
                prev_month_text="<< " + Month(),
                next_month_text=Month() + " >>",
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                this_month_text="[" + Month() + "]",
                month_text=Month()
            ),
            CalendarScope.YEARS: CalendarYearsView(self._item_callback_data),
        }
    
    async def _render_keyboard(
            self,
            data,
            manager: DialogManager,
    ) -> RawKeyboard:
        scope = self.get_scope(manager)
        view = self.views[scope]
        offset = self.get_offset(manager)
        config = self.config.merge(await self._get_user_config(data, manager))
        if offset is None:
            offset = datetime.now(ZoneInfo("Europe/Vilnius")).date()
            self.set_offset(offset, manager)
        offset = offset.replace(day=1)
        self.set_offset(offset, manager)
  # безопасно всегда стартовать с первого числа месяца

        return await view.render(config, offset, data, manager)

    # async def _get_user_config(
    #         self,
    #         data: dict,
    #         manager: DialogManager,
    # ) -> CalendarUserConfig:
    #     return CalendarUserConfig(
    #         firstweekday=7,
    #         max_date=date(2015, 12, 31)
    #     )