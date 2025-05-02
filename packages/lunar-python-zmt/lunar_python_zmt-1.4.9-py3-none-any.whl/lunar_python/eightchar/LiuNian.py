# -*- coding: utf-8 -*-
from . import LiuYue
from ..util import LunarUtil


class LiuNian:
    """
    流年
    """

    def __init__(self, da_yun, index):
        self.__daYun = da_yun
        self.__lunar = da_yun.getLunar()
        self.__index = index
        self.__year = da_yun.getStartYear() + index
        self.__age = da_yun.getStartAge() + index

    def getIndex(self):
        return self.__index

    def getYear(self):
        return self.__year

    def getAge(self):
        return self.__age

    def getGanZhi(self):
        """
        获取干支
        :return: 干支
        """
        offset = LunarUtil.getJiaZiIndex(self.__lunar.getJieQiTable()["立春"].getLunar().getYearInGanZhiExact()) + self.__index
        if self.__daYun.getIndex() > 0:
            offset += self.__daYun.getStartAge() - 1
        offset %= len(LunarUtil.JIA_ZI)
        return LunarUtil.JIA_ZI[offset]

    def getXun(self):
        """
        获取所在旬
        :return: 旬
        """
        return LunarUtil.getXun(self.getGanZhi())

    def getXunKong(self):
        """
        获取旬空(空亡)
        :return: 旬空(空亡)
        """
        return LunarUtil.getXunKong(self.getGanZhi())

    def getLiuYue(self):
        """
        获取流月
        :return: 流月
        """
        n = 12
        liu_yue = []
        for i in range(0, n):
            liu_yue.append(LiuYue(self, i))
        return liu_yue

    def getShiShen(self, gan: str):
        """
        获取天干十神
        :param gan: 日元
        :return: 十神
        """
        return LunarUtil.SHI_SHEN.get(gan + self.getGanZhi()[0])
    
    def getShiShenShort(self, gan: str):
        """
        获取天干十神简称
        :param gan: 日元
        :return: 十神简称
        """
        return LunarUtil.SHI_SHEN_SHORT.get(gan + self.getGanZhi()[0])
    
    def getCangGan(self):
        """
        获取藏干
        :return: 藏干
        """
        return LunarUtil.ZHI_HIDE_GAN.get(self.getGanZhi()[1])
    
    def getCangGanShiShenShort(self, gan: str):
        """
        获取藏干十神简称
        :param gan: 日元
        :return: 藏干十神简称
        """
        cg = LunarUtil.ZHI_HIDE_GAN.get(self.getGanZhi()[1])
        arr = []
        for cg_gan in cg:
            arr.append(LunarUtil.SHI_SHEN_SHORT.get(gan + cg_gan))
        return arr

    def getCangGanShiShen(self, gan: str):
        """
        获取藏干十神
        :param gan: 日元
        :return: 藏干十神
        """
        cg = LunarUtil.ZHI_HIDE_GAN.get(self.getGanZhi()[1])
        arr = []
        for cg_gan in cg:
            arr.append(LunarUtil.SHI_SHEN.get(gan + cg_gan))
        return arr