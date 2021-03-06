#!/usr/bin/env python
# -*- coding: utf-8 -*-
from source.strategy.mystrategy import strategy_list

class StrategyManager(object):
    def __init__(self, config_client, outgoing_request_event_engine, order_manager, portfolio_manager):
        self._config_client = config_client
        self._outgoing_request_event_engine = outgoing_request_event_engine
        self._order_manager = order_manager    # get sid from
        self._portfolio_manager = portfolio_manager
        self._strategy_id = 1
        self._strategy_dict = {}            # strategy_id ==> strategy
        # there could be more than one strategy that subscribes to a symbol
        self._tick_strategy_dict = {}  # sym -> list of strategy
        self.sid_oid_dict = {}  # sid => list of order id
        self.reset()

    def reset(self):
        self._strategy_id = 1          # 0 is mannual discretionary trade
        self._strategy_dict.clear()
        self.sid_oid_dict.clear()

    def load_strategy(self):
        for s in self._config_client['strategy']:
            strategyClass = strategy_list.get(s, None)
            if not strategyClass:
                print(u'can not find strategy：%s' % s)
            else:
                strategy = strategyClass(self._outgoing_request_event_engine)
                strategy.id = self._strategy_id
                strategy.name = s          # assign class name to the strategy

                # init strategy
                strategy.on_init(self._config_client['strategy'][s])
                for sym in strategy.symbols:
                    if sym in self._tick_strategy_dict:
                        self._tick_strategy_dict[sym].append(self._strategy_id)
                    else:
                        self._tick_strategy_dict[sym] = [self._strategy_id]

                strategy.active = False
                self._strategy_dict[self._strategy_id] = strategy
                self._strategy_id = self._strategy_id+1

    def start_strategy(self, sid):
        self._strategy_dict[sid].on_start()

    def stop_strategy(self, sid):
        self._strategy_dict[sid].on_stop()

    def pause_strategy(self, sid):
        pass

    def flat_strategy(self, sid):
        pass

    def start_all(self):
        pass

    def stop_all(self):
        pass

    def flat_all(self):
        pass

    def cancel_all(self):
        pass

    def on_tick(self, k):
        if k.full_symbol in self._tick_strategy_dict:
            # foreach strategy that subscribes to this tick
            s_list = self._tick_strategy_dict[k.full_symbol]
            for sid in s_list:
                if self._strategy_dict[sid].active:
                    self._strategy_dict[sid].on_tick(k)

    def on_position(self, pos):
        pass

    def on_order_status(self, os):
        if os.client_order_id in self._oid_sid_dict:
            self._strategies_dict[os.client_order_id].on_order_status(os)
        else:
            print('strategy manager doesnt hold the oid, possibly from outside of the system')

    def on_cancel(self, oid):
        pass

    def on_fill(self, fill):
        pass