/* Copyright (C) 2022 Patrick Ziegler
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

create view if not exists monthly_breakdown AS
select t1.month, t3.income, k1.groceries, k2.restaurants,
	IFNULL(t2.expenses, 0.0) - IFNULL(k1.groceries, 0.0) - IFNULL(k2.restaurants, 0.0) as others,
	IFNULL(t2.expenses, 0.0) + IFNULL(t3.income, 0.0) as saldo from (
		select strftime("%Y-%m", date) as month from __transactions__
		group by month
	) t1 left join (
		select strftime("%Y-%m", date) as month, sum(value) as groceries from __transactions__ T
		inner join monthly_breakdown_keys_groceries K on T.description like K.description
		group by month
	) k1 on k1.month = t1.month left join (
		select strftime("%Y-%m", date) as month, sum(value) as restaurants from __transactions__ T
		inner join monthly_breakdown_keys_restaurants K on T.description like K.description
		group by month
	) k2 on k2.month = t1.month left join (
		select strftime("%Y-%m", date) as month,  sum(value) as expenses from __transactions__ T
		where T.value < 0 group by month
	) t2 on t2.month = t1.month left join (
		select strftime("%Y-%m", date) as month,  sum(value) as income from __transactions__ T
		where T.value > 0 group by month
	) t3 on t3.month = t1.month
	order by t1.month desc;
