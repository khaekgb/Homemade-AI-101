class trading_env:
    def __init__(self, obs_data_len, step_len,epi,
                 df, fee, max_position=5, deal_col_name='price', plot_col_name='middle',
                 feature_names=['price', 'volume'], 
                 return_transaction=True ):#,
                #  fluc_div=100.0, gameover_limit=5,
                #  *args, **kwargs):

        self.df = df
        # self.action_space = 4
        # self.action_space = spaces.Discrete(3)
        self.action_describe = {0:'do nothing',  1:'long', 2:'short' , 3 :'close all'}
        
        self.obs_len = obs_data_len
        # self.feature_len = len(feature_names)
        self.feature_len = len(feature_names)  # return_transaction

        self.using_feature = feature_names
        self.price_name = deal_col_name
        self.price_plot = plot_col_name
        
        self.step_len = step_len
        self.fee = fee
        self.max_position = max_position
        
        self.return_transaction = return_transaction
        
        self.begin_fs = self.df[self.df['serial_number']==0]
        self.date_leng = len(self.begin_fs)
        
        self.render_on = 0
        self.buy_color, self.sell_color = (1, 2)
        self.new_rotation, self.cover_rotation = (1, 2)
        self.transaction_details = pd.DataFrame()
        self.epi = epi
    
    def _random_choice_section(self):
        random_int = np.random.randint(self.date_leng)
        if random_int == self.date_leng - 1:
            begin_point = self.begin_fs.index[random_int]
            end_point = None
        else:
            begin_point, end_point = self.begin_fs.index[random_int: random_int+2]
        df_section = self.df.iloc[begin_point: end_point]
        return df_section

    def reset(self):
        self.df_sample = self._random_choice_section()
        self.step_st = 0

        # define the price to calculate the reward
        self.price = self.df_sample[self.price_name].as_matrix()
        # define the price to plot BB
        self.price_mid = self.df_sample[self.price_plot].as_matrix()     #######################

        # define the observation feature
        self.obs_features = self.df_sample[self.using_feature].as_matrix()

        ####################### StandardScaler StandardScaler StandardScaler StandardScaler StandardScaler StandardScaler StandardScaler StandardScaler

        scaler = preprocessing.StandardScaler()
        self.obs_features = scaler.fit_transform(self.obs_features)

        # maybe make market position feature in final feature, set as option
        self.posi_arr = np.zeros_like(self.price)
        # position variation
        self.posi_variation_arr = np.zeros_like(self.posi_arr)
        # position entry or cover :new_entry->1  increase->2 cover->-1 decrease->-2
        self.posi_entry_cover_arr = np.zeros_like(self.posi_arr)
        
        self.price_mean_arr = self.price.copy()
        self.reward_fluctuant_arr = (self.price - self.price_mean_arr)*self.posi_arr
        self.reward_makereal_arr = self.posi_arr.copy()
        self.reward_arr = self.reward_fluctuant_arr*self.reward_makereal_arr

        self.info = None
        self.transaction_details = pd.DataFrame()
        
        # observation part
        self.obs_state = self.obs_features[self.step_st: self.step_st+self.obs_len]

        self.obs_posi = self.posi_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_posi_var = self.posi_variation_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_posi_entry_cover = self.posi_entry_cover_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_price = self.price[self.step_st: self.step_st+self.obs_len]
        self.obs_price_mean = self.price_mean_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_reward_fluctuant = self.reward_fluctuant_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_makereal = self.reward_makereal_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_reward = self.reward_arr[self.step_st: self.step_st+self.obs_len]
        
        if self.return_transaction:
            # self.obs_return = np.concatenate((self.obs_state, 
            #                                 self.obs_posi[:, np.newaxis], 
            #                                 self.obs_posi_var[:, np.newaxis],
            #                                 self.obs_posi_entry_cover[:, np.newaxis],
            #                                 self.obs_price[:, np.newaxis],
            #                                 self.obs_price_mean[:, np.newaxis],
            #                                 self.obs_reward_fluctuant[:, np.newaxis] ,
            #                                 self.obs_makereal[:, np.newaxis],
            #                                 self.obs_reward[:, np.newaxis] ), axis=1)

            scaler = preprocessing.StandardScaler()
            self.obs_return = np.concatenate((self.obs_state, scaler.fit_transform(np.concatenate((self.obs_posi[:, np.newaxis] 
                                                                                                    ,self.obs_posi_var[:, np.newaxis] 
                                                                                                    ,self.obs_posi_entry_cover[:, np.newaxis]
                                                                                                    ,self.obs_price[:, np.newaxis]       
                                                                                                    ,self.obs_price_mean[:, np.newaxis]
                                                                                                    ,self.obs_reward_fluctuant[:, np.newaxis]
                                                                                                    ,self.obs_makereal[:, np.newaxis]
                                                                                                    ,self.obs_reward[:, np.newaxis]
                                                                                                    ) , axis=1) ) )  , axis=1 ) 
        else:
            self.obs_return = self.obs_state

        self.t_index = 0

        return self.obs_return
    
    def _long(self, open_posi, enter_price, current_mkt_position, current_price_mean):
        if open_posi:
            self.chg_price_mean[:] = enter_price
            self.chg_posi[:] = 1
            self.chg_posi_var[:1] = 1
            self.chg_posi_entry_cover[:1] = 1
        else:
            after_act_mkt_position = current_mkt_position + 1
            self.chg_price_mean[:] = (current_price_mean*current_mkt_position + \
                                        enter_price)/after_act_mkt_position
            self.chg_posi[:] = after_act_mkt_position
            self.chg_posi_var[:1] = 1
            self.chg_posi_entry_cover[:1] = 2
            
    def _short(self, open_posi, enter_price, current_mkt_position, current_price_mean):
        if open_posi:
            self.chg_price_mean[:] = enter_price
            self.chg_posi[:] = -1
            self.chg_posi_var[:1] = -1
            self.chg_posi_entry_cover[:1] = 1
        else:
            after_act_mkt_position = current_mkt_position - 1
            self.chg_price_mean[:] = (current_price_mean*abs(current_mkt_position) + \
                                      enter_price)/abs(after_act_mkt_position)
            self.chg_posi[:] = after_act_mkt_position
            self.chg_posi_var[:1] = -1
            self.chg_posi_entry_cover[:1] = 2
          
    def _short_cover(self, current_price_mean, current_mkt_position):
        self.chg_price_mean[:] = current_price_mean
        self.chg_posi[:] = current_mkt_position + 1
        self.chg_makereal[:1] = 1
        self.chg_reward[:] = ((self.chg_price - self.chg_price_mean)*(-1) - self.fee)*self.chg_makereal
        self.chg_posi_var[:1] = 1
        self.chg_posi_entry_cover[:1] = -1
    
    def _long_cover(self, current_price_mean, current_mkt_position):
        self.chg_price_mean[:] = current_price_mean
        self.chg_posi[:] = current_mkt_position - 1
        self.chg_makereal[:1] = 1
        self.chg_reward[:] = ((self.chg_price - self.chg_price_mean)*(1) - self.fee)*self.chg_makereal
        self.chg_posi_var[:1] = -1
        self.chg_posi_entry_cover[:1] = -1
    
    def _stayon(self, current_price_mean, current_mkt_position):
        self.chg_posi[:] = current_mkt_position
        self.chg_price_mean[:] = current_price_mean

    def _close_all(self, current_price_mean, current_mkt_position):
            self.chg_price_mean[:] = current_price_mean
            self.chg_posi[:] = 0
            self.chg_posi_var[:1] = -current_mkt_position
            self.chg_posi_entry_cover[:1] = -2
            self.chg_makereal[:1] = 1
            self.chg_reward[:] = ((self.chg_price - self.chg_price_mean)*(current_mkt_position) - abs(current_mkt_position)*self.fee)*self.chg_makereal

    def step(self, action):
        current_index = self.step_st + self.obs_len -1
        current_price_mean = self.price_mean_arr[current_index]
        current_mkt_position = self.posi_arr[current_index]

        self.t_index += 1
        self.step_st += self.step_len

        # observation part
        self.obs_state = self.obs_features[self.step_st: self.step_st+self.obs_len]
        self.obs_posi = self.posi_arr[self.step_st: self.step_st+self.obs_len]

        # position variation
        self.obs_posi_var = self.posi_variation_arr[self.step_st: self.step_st+self.obs_len]

        # position entry or cover :new_entry->1  increase->2 cover->-1 decrease->-2
        self.obs_posi_entry_cover = self.posi_entry_cover_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_price = self.price[self.step_st: self.step_st+self.obs_len]
        self.obs_price_mean = self.price_mean_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_reward_fluctuant = self.reward_fluctuant_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_makereal = self.reward_makereal_arr[self.step_st: self.step_st+self.obs_len]
        self.obs_reward = self.reward_arr[self.step_st: self.step_st+self.obs_len]

        # change part
        self.chg_posi = self.obs_posi[-self.step_len:]
        self.chg_posi_var = self.obs_posi_var[-self.step_len:]
        self.chg_posi_entry_cover = self.obs_posi_entry_cover[-self.step_len:]
        self.chg_price = self.obs_price[-self.step_len:]
        self.chg_price_mean = self.obs_price_mean[-self.step_len:]
        self.chg_reward_fluctuant = self.obs_reward_fluctuant[-self.step_len:]
        self.chg_makereal = self.obs_makereal[-self.step_len:]
        self.chg_reward = self.obs_reward[-self.step_len:]

        done = False
        if self.step_st+self.obs_len+self.step_len >= len(self.price):
            done = True
            action = -1
            if current_mkt_position != 0:
                self.chg_price_mean[:] = current_price_mean
                self.chg_posi[:] = 0
                self.chg_posi_var[:1] = -current_mkt_position
                self.chg_posi_entry_cover[:1] = -2
                self.chg_makereal[:1] = 1
                self.chg_reward[:] = ((self.chg_price - self.chg_price_mean)*(current_mkt_position) - abs(current_mkt_position)*self.fee)*self.chg_makereal

            self.transaction_details = pd.DataFrame([self.posi_arr,
                                                     self.posi_variation_arr,
                                                     self.posi_entry_cover_arr,
                                                     self.price_mean_arr,
                                                     self.reward_fluctuant_arr,
                                                     self.reward_makereal_arr,
                                                     self.reward_arr], 
                                                     index=['position', 'position_variation', 'entry_cover',
                                                            'price_mean', 'reward_fluctuant', 'reward_makereal',
                                                            'reward'], 
                                                     columns=self.df_sample.index).T

            self.info = self.df_sample.join(self.transaction_details)  # Original

            
        # use next tick, maybe choice avg in first 10 tick will be better to real backtest
        enter_price = self.chg_price[0]
        if action == 1 and self.max_position > current_mkt_position >= 0:
            open_posi = (current_mkt_position == 0)
            self._long(open_posi, enter_price, current_mkt_position, current_price_mean)
        
        elif action == 2 and -self.max_position < current_mkt_position <= 0:
            open_posi = (current_mkt_position == 0)
            self._short(open_posi, enter_price, current_mkt_position, current_price_mean)
        
        elif action == 1 and current_mkt_position < 0:
            self._short_cover(current_price_mean, current_mkt_position)

        elif action == 2 and current_mkt_position > 0:
            self._long_cover(current_price_mean, current_mkt_position)

        ###########################################################################################################
        # elif action == 0 and current_mkt_position != 0:
        #     self._close_all(current_price_mean, current_mkt_position)
        ###########################################################################################################

        elif action == 1 and current_mkt_position==self.max_position:
            action = 0

        elif action == 2 and current_mkt_position==-self.max_position:
            action = 0

        # elif action == 3 and current_mkt_position == 0:
        #     action = 0

        if action == 0:
            if current_mkt_position != 0:
                self._stayon(current_price_mean, current_mkt_position)


        self.chg_reward_fluctuant[:] = (self.chg_price - self.chg_price_mean)*self.chg_posi - np.abs(self.chg_posi)*self.fee

        if self.return_transaction:
            # self.obs_return = np.concatenate((self.obs_state, 
            #                                 self.obs_posi[:, np.newaxis] ,                  # 1
            #                                 self.obs_posi_var[:, np.newaxis],              # 2
            #                                 self.obs_posi_entry_cover[:, np.newaxis],      # 3
            #                                 self.obs_price[:, np.newaxis],                 # 4
            #                                 self.obs_price_mean[:, np.newaxis],            # 5
            #                                 self.obs_reward_fluctuant[:, np.newaxis],     # 6
            #                                 self.obs_makereal[:, np.newaxis],              # 7
            #                                 self.obs_reward[:, np.newaxis]), axis=1)      # 8

            scaler = preprocessing.StandardScaler()
            self.obs_return = np.concatenate((self.obs_state, scaler.fit_transform(np.concatenate((self.obs_posi[:, np.newaxis] 
                                                                                                    ,self.obs_posi_var[:, np.newaxis] 
                                                                                                    ,self.obs_posi_entry_cover[:, np.newaxis]
                                                                                                    ,self.obs_price[:, np.newaxis]       
                                                                                                    ,self.obs_price_mean[:, np.newaxis]
                                                                                                    ,self.obs_reward_fluctuant[:, np.newaxis]
                                                                                                    ,self.obs_makereal[:, np.newaxis]
                                                                                                    ,self.obs_reward[:, np.newaxis]
                                                                                                    ) , axis=1) ) )  , axis=1 ) 
   
        else:
            self.obs_return = self.obs_state

        # return self.obs_return, self.obs_reward.sum(), done, self.info   # Original
        return self.obs_return , self.obs_reward[0], done ,self.obs_reward_fluctuant[0] ,self.obs_posi[0] ,self.info
                                    ###########################################################

    def _gen_trade_color(self, ind, long_entry=(0, 1, 0, 0.8), long_cover=(1, 1, 1, 0.5), 
                         short_entry=(1, 0, 0, 0.8), short_cover=(1, 1, 1, 0.5)): 
        if self.posi_variation_arr[ind]>0 and self.posi_entry_cover_arr[ind]>0:
            return long_entry
        elif self.posi_variation_arr[ind]>0 and self.posi_entry_cover_arr[ind]<0:
            return long_cover
        elif self.posi_variation_arr[ind]<0 and self.posi_entry_cover_arr[ind]>0:
            return short_entry
        elif self.posi_variation_arr[ind]<0 and self.posi_entry_cover_arr[ind]<0:
            return short_cover 
    
    def _plot_trading(self):
        price_x = list(range(len(self.price[:self.step_st+self.obs_len])))
        price_ma = list(range(len(self.price_mid[:self.step_st+self.obs_len])))  ###############

        self.price_plot = self.ax.plot(price_x, self.price[:self.step_st+self.obs_len], c=(0, 0.68, 0.95, 0.9),zorder=1)
        self.price_plot2 = self.ax.plot(price_ma, self.price_mid[:self.step_st+self.obs_len], c=(0.5, 0, 0, 0.2),zorder=1) ###############

        # maybe seperate up down color
        #self.price_plot = self.ax.plot(price_x, self.price[:self.step_st+self.obs_len], c=(0, 0.75, 0.95, 0.9),zorder=1)
        # self.features_plot = [self.ax3.plot(price_x, self.obs_features[:self.step_st+self.obs_len, i], 
        #                                     c=self.features_color[i])[0] for i in range(self.feature_len)]
        rect_high = self.obs_price.max() - self.obs_price.min()
        self.target_box = self.ax.add_patch(
                            patches.Rectangle(
                            (self.step_st, self.obs_price.min()), self.obs_len, rect_high,
                            label='observation',edgecolor=(0.9, 1, 0.2, 0.8),facecolor=(0.95,1,0.1,0.1),
                            linestyle='-',linewidth=1.5,
                            fill=True)
                            )     # remove background)
        self.fluc_reward_plot_p = self.ax2.fill_between(price_x, 0, self.reward_fluctuant_arr[:self.step_st+self.obs_len],
                                                        where=self.reward_fluctuant_arr[:self.step_st+self.obs_len]>=0, 
                                                        facecolor=(1, 0.8, 0, 0.2), edgecolor=(1, 0.8, 0, 0.9), linewidth=0.8)
        self.fluc_reward_plot_n = self.ax2.fill_between(price_x, 0, self.reward_fluctuant_arr[:self.step_st+self.obs_len],
                                                        where=self.reward_fluctuant_arr[:self.step_st+self.obs_len]<=0, 
                                                        facecolor=(0, 1, 0.8, 0.2), edgecolor=(0, 1, 0.8, 0.9), linewidth=0.8)
        self.posi_plot_long = self.ax3.fill_between(price_x, 0, self.posi_arr[:self.step_st+self.obs_len], 
                                                    where=self.posi_arr[:self.step_st+self.obs_len]>=0, 
                                                    facecolor=(1, 0.5, 0, 0.2), edgecolor=(1, 0.5, 0, 0.9), linewidth=1)
        self.posi_plot_short = self.ax3.fill_between(price_x, 0, self.posi_arr[:self.step_st+self.obs_len], 
                                                     where=self.posi_arr[:self.step_st+self.obs_len]<=0, 
                                                     facecolor=(0, 0.5, 1, 0.2), edgecolor=(0, 0.5, 1, 0.9), linewidth=1)
        self.reward_plot_p = self.ax2.fill_between(price_x, 0, 
                                                   self.reward_arr[:self.step_st+self.obs_len].cumsum(),
                                                   where=self.reward_arr[:self.step_st+self.obs_len].cumsum()>=0,
                                                   facecolor=(0, 1, 0, 0.2), edgecolor=(0, 1, 0, 0.9), linewidth=1)
        self.reward_plot_n = self.ax2.fill_between(price_x, 0, 
                                                   self.reward_arr[:self.step_st+self.obs_len].cumsum(),
                                                   where=self.reward_arr[:self.step_st+self.obs_len].cumsum()<=0,
                                                   facecolor=(1, 0, 0, 0.2), edgecolor=(1, 0, 0, 0.9), linewidth=1)

        trade_x = self.posi_variation_arr.nonzero()[0]
        trade_x_buy = [i for i in trade_x if self.posi_variation_arr[i]>0]
        trade_x_sell = [i for i in trade_x if self.posi_variation_arr[i]<0]
        trade_y_buy = [self.price[i] for i in trade_x_buy]
        trade_y_sell =  [self.price[i] for i in trade_x_sell]
        trade_color_buy = [self._gen_trade_color(i) for i in trade_x_buy] 
        trade_color_sell = [self._gen_trade_color(i) for i in trade_x_sell]
        self.trade_plot_buy = self.ax.scatter(x=trade_x_buy, y=trade_y_buy, s=100, marker='^', 
                                              c=trade_color_buy, edgecolors=(0,1,0,0.4), zorder=2)
        self.trade_plot_sell = self.ax.scatter(x=trade_x_sell, y=trade_y_sell, s=100, marker='v', 
                                               c=trade_color_sell, edgecolors=(1,0,0,0.4), zorder=2)

    def render(self, save=True):
        if self.render_on == 0:
            matplotlib.style.use('dark_background')
            self.render_on = 1

            left, width = 0.1, 0.8
            rect1 = [left, 0.42, width, 0.55]
            rect2 = [left, 0.12, width, 0.3]
            rect3 = [left, 0.01, width, 0.11]

            self.fig = plt.figure(figsize=(15,8))
            self.fig.suptitle('%s'%self.df_sample['datetime'].iloc[0].date(), fontsize=14, fontweight='bold')
            # self.ax = self.fig.add_subplot(1,1,1)
            self.ax = self.fig.add_axes(rect1)  # left, bottom, width, height
            self.ax2 = self.fig.add_axes(rect2, sharex=self.ax)
            self.ax3 = self.fig.add_axes(rect3, sharex=self.ax)
            self.ax.grid(color='gray', linestyle='-', linewidth=0.5)
            self.ax2.grid(color='gray', linestyle='-', linewidth=0.5)
            self.ax3.grid(color='gray', linestyle='-', linewidth=0.5)
            self.features_color = [c.rgb+(0.9,) for c in Color('yellow').range_to(Color('cyan'), self.feature_len)]
            #fig, ax = plt.subplots()
            self._plot_trading()

            self.ax.set_xlim(0,len(self.price[:self.step_st+self.obs_len])+200)
            # plt.ion()
            #self.fig.tight_layout()
            # plt.show()
            # if save :
                # if self.step_st+self.obs_len+self.step_len >= len(self.price):
                # self.fig.savefig('cartpole/3-reinforce/save_graph/rr%s.png' % str(self.epi))
                    # self.fig.savefig('cartpole/3-reinforce/save_graph/a_%s.png' % str(self.epi))

        elif self.render_on == 1:
            self.ax.lines.remove(self.price_plot[0])
            # [self.ax3.lines.remove(plot) for plot in self.features_plot]
            self.fluc_reward_plot_p.remove()
            self.fluc_reward_plot_n.remove()
            self.target_box.remove()
            self.reward_plot_p.remove()
            self.reward_plot_n.remove()
            self.posi_plot_long.remove()
            self.posi_plot_short.remove()
            self.trade_plot_buy.remove()
            self.trade_plot_sell.remove()

            self._plot_trading()

            self.ax.set_xlim(0,len(self.price[:self.step_st+self.obs_len])+200)
            if save and (self.step_st+self.obs_len+self.step_len) >= (len(self.price)-self.step_len) :
                # if self.step_st+self.obs_len+self.step_len >= len(self.price):
                # self.fig.savefig('cartpole/3-reinforce/save_graph/rr%s.png' % str(self.epi))
                    self.fig.savefig('cartpole/3-reinforce/save_graph/a_%s.png' % str(self.epi))
                    print(self.step_st+self.obs_len+self.step_len , len(self.price)-self.step_len)
            plt.pause(0.0001)