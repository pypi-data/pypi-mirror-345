#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by dmitrii at 05.01.2025

"""
Этот модуль предоставляет класс Expanding для обратной совместимости.
В текущей версии библиотеки Expanding был переименован в RowExpanding.
"""

from .row_expanding import RowExpanding

# Для обратной совместимости
Expanding = RowExpanding

__all__ = ["Expanding"] 