import datetime
import os
import spacy
from spacy.lang.vi import Vietnamese
from spacy.lang.en import English
import requests
import json
import numpy as np
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
import logging
import re
from underthesea import text_normalize
from .init_data import JSON_DATA_STR, ADDITIONAL_DATA
FAILURE_SYMBOLS_ORIGINAL = ["MTV", "USD", "CEO", "HCM", "TIP", "APP", "AMD", "CAR", "CLG", "DNA", "FOX", "SBS", 'PGD', 'CNN', 'SJC', 'BOT', 'PPP', 'AAA', 'VND', 'CPI', 'CMC', 'NAV', 'SMA', 'TIN', "TOP"]
FAILURE_SYMBOLS = ["Tin", "tin", 'SMA', 'TIN', 'HOT']
PRE_TOKEN = ['cp', 'ma', 'mã', 'cổ phiếu']
LAST_ORDER_SYMBOLS = ["CEO", "PGD", "TOP"]


class QuestionSymbolDetector:
    def __init__(self, num_date_expire: int=1):
        self.symbol2info = {}
        self.symbols = []
        self.fullname2symbol = {}
        self.additionalsymbol2name = {}
        self.symbolinname = {}
        self.symbolinname2symbols = {}
        self.fullname = []
        self.nlp = English()
        self.nlp_vietnamese = spacy.load('vi_core_news_lg')
        self.num_date_expire = num_date_expire
        self.curr_created_date = None
        self.is_updating = False
        self.derivative_mapping_data = {}
        try:
            self.get_info()
        except:
            pass
        self.symbol_patterns = [{"LOWER": {"IN": [sym.lower() for sym in self.symbols]}}]
        self.full_name_patterns = [
            self.nlp.make_doc(name) for name in list(self.fullname)
        ]

    def get_info(self):
        for comp in ADDITIONAL_DATA:
            symbol = comp['symbol']
            name = comp['name']
            if symbol not in self.additionalsymbol2name:
                self.additionalsymbol2name[symbol] = []
            self.additionalsymbol2name[symbol].append(name)

        JSON_DATA = json.loads(JSON_DATA_STR)
        self.curr_created_date = datetime.datetime.strptime(JSON_DATA['created_date'], '%Y-%m-%d')
        for comp in JSON_DATA['data']:
            if len(comp["symbol"].strip()) != 3:
                continue
            info = {
                "symbol": comp["symbol"],
                "name": text_normalize(comp["name"]) if comp["name"] is not None else comp["name"],
                "full_name": text_normalize(comp["companyName"]),
            }
            # set pair normalize company to symbol
            temp_fullname2symbol, temp_fullname = self.normalize_company_name2symbol(info)
            self.fullname += temp_fullname
            self.fullname2symbol.update(temp_fullname2symbol)
            # check valid symbols
            self.symbols.append(comp["symbol"])
            # company info
            self.symbol2info[comp["symbol"]] = info

        for key in self.symbols:
            full_name = [t.text for t in self.nlp(self.symbol2info[key]["full_name"])]
            try:
                name = [t.text for t in self.nlp(self.symbol2info[key]["name"])]
            except:
                name = []
            for okey in self.symbols:
                if okey == key:
                    continue
                if len(name)>0 and okey in name:
                    if okey not in self.symbolinname:
                        self.symbolinname[okey] = []
                        self.symbolinname2symbols[okey] = []
                    self.symbolinname[okey].append((key, name))
                    self.symbolinname2symbols[okey].append(key)
                if okey in full_name:
                    if okey not in self.symbolinname:
                        self.symbolinname[okey] = []
                        self.symbolinname2symbols[okey] = []
                    self.symbolinname[okey].append((key, full_name))
                    self.symbolinname2symbols[okey].append(key)
        
        for other_key in self.additionalsymbol2name:
            if other_key not in self.symbols:
                self.symbols.append(other_key)

    def update_data(self):
        try:
            json_data = None
            try:
                json_data = requests.get('https://api.dnse.com.vn/market-api/tickers?_end=10000').json()
            except:
                pass
            self.additionalsymbol2name = {}
            symbols = []
            symbol2info = {}
            fullname = []
            fullname2symbol = {}
            symbolinname = {}
            symbolinname2symbols = {}

            for comp in ADDITIONAL_DATA:
                symbol = comp['symbol']
                name = comp['name']
                if symbol not in self.additionalsymbol2name:
                    self.additionalsymbol2name[symbol] = []
                self.additionalsymbol2name[symbol].append(name)
            # get infor to detect symbol
            if json_data is not None:
                for comp in json_data['data']:
                    if len(comp["symbol"].strip()) != 3:
                        continue
                    info = {
                        "symbol": comp["symbol"],
                        "name": text_normalize(comp["name"]) if comp["name"] is not None else comp["name"],
                        "full_name": text_normalize(comp["companyName"]),
                    }
                    # set pair normalize company to symbol
                    temp_fullname2symbol, temp_fullname = self.normalize_company_name2symbol(info)
                    fullname += temp_fullname
                    fullname2symbol.update(temp_fullname2symbol)
                    # check valid symbols
                    symbols.append(comp["symbol"])
                    # company info
                    symbol2info[comp["symbol"]] = info

                for key in symbols:
                    full_name = [t.text for t in self.nlp(symbol2info[key]["full_name"])]
                    try:
                        name = [t.text for t in self.nlp(symbol2info[key]["name"])]
                    except:
                        name = []
                    for okey in symbols:
                        if okey == key:
                            continue
                        if len(name)>0 and okey in name:
                            if okey not in symbolinname:
                                symbolinname[okey] = []
                                symbolinname2symbols[okey] = []
                            symbolinname[okey].append((key, name))
                            symbolinname2symbols[okey].append(key)
                        if okey in full_name:
                            if okey not in symbolinname:
                                symbolinname[okey] = []
                                symbolinname2symbols[okey] = []
                            symbolinname[okey].append((key, full_name))
                            symbolinname2symbols[okey].append(key)
                self.symbol2info = symbol2info
                self.symbols = symbols
                self.fullname2symbol = fullname2symbol
                self.symbolinname = symbolinname
                self.symbolinname2symbols = symbolinname2symbols
                self.fullname = fullname

                for other_key in self.additionalsymbol2name:
                    if other_key not in self.symbols:
                        self.symbols.append(other_key)
                self.symbol_patterns = [{"LOWER": {"IN": [sym.lower() for sym in self.symbols]}}]
                self.full_name_patterns = [
                    self.nlp.make_doc(name) for name in list(self.fullname)
                ]
                self.is_updating = False
                self.curr_created_date = datetime.datetime.now()
                
        except Exception as e:
            raise e
        
    def normalize_company_name2symbol(self, info):
        
        if '- CTCP' in info["full_name"]:
            full_name = info["full_name"].replace('- CTCP','').strip()
        elif 'CTCP Tập' in info["full_name"]:
            full_name = info["full_name"].replace('CTCP Tập','Tập').strip()
        else:
            full_name = info["full_name"].strip()
        full_name = full_name.replace('-', ' - ')
        full_name = full_name.replace('(', ' ( ')
        full_name = full_name.replace(')', ' ) ')
        full_name = full_name.replace('.', ' . ')
        full_name = re.sub(' +',' ', full_name).strip()


        list_renamed = []
        list_renamed.append(full_name)
        ##
        if "CTCP" in full_name:
            list_renamed.append(full_name.replace("CTCP", "công ty cổ phần").strip())
            list_renamed.append(full_name.replace("CTCP", "Công ty cổ phần").strip())
            list_renamed.append(full_name.replace("CTCP", "công ty Cổ phần").strip())
            list_renamed.append(full_name.replace("CTCP", "Công ty Cổ phần").strip())

        ##
        if "TMCP" in full_name:
            list_renamed.append(full_name.replace("TMCP", "thương mại cổ phần").strip())
            list_renamed.append(full_name.replace("TMCP", "Thương mại cổ phần").strip())
            list_renamed.append(full_name.replace("TMCP", "thương mại Cổ phần").strip())
            list_renamed.append(full_name.replace("TMCP", "Thương mại Cổ phần").strip())

        ##
        if "TNHH" in full_name:
            list_renamed.append(full_name.replace("TNHH", "trách nhiệm hữu hạn").strip())
            list_renamed.append(full_name.replace("TNHH", "Trách nhiệm hữu hạn").strip())
            list_renamed.append(full_name.replace("TNHH", "trách nhiệm Hữu hạn").strip())
            list_renamed.append(full_name.replace("TNHH", "Trách nhiệm Hữu hạn").strip())

        ##
        if "MTV" in full_name:
            list_renamed.append(full_name.replace("MTV", "một thành viên").strip())
            list_renamed.append(full_name.replace("MTV", "một Thành viên").strip())
            list_renamed.append(full_name.replace("MTV", "Một thành viên").strip())
            list_renamed.append(full_name.replace("MTV", "Một Thành viên").strip())

        if " CP " in full_name:
            list_renamed.append(full_name.replace(" CP ", " cổ phần ").strip())
            list_renamed.append(full_name.replace(" CP ", " Cổ phần ").strip())
        
        if "Chứng khoán" in full_name:
            list_renamed.append(full_name.replace("CTCP ", "").strip())
            list_renamed.append(full_name.replace("CTCP Chứng khoán", "CTCK").strip())

        if info["symbol"] in self.additionalsymbol2name:
            for name in self.additionalsymbol2name[info["symbol"]]:
                list_renamed.append(name)
        
        other_name = []
        # modified full name
        other_name.append(full_name.replace('CTCP ', '').strip().replace('- CTCP', '').strip())
        other_name.append(other_name[-1].replace('Tập đoàn', '').strip())
        # modified name
        name = info['name']
        if name is not None:
            temp = []
            for word in name.replace('- JSC','').split(' '):
                temp += word.split('.,')
            if len(temp)>=1:
                new_name = []
                for word in temp:
                    if word.strip().lower() not in ['jsc', 'corp', 'corporation', 'group']:
                        new_name.append(word)
                other_name.append(' '.join(new_name).strip())
            for word in other_name:
                if word not in list_renamed and word != info["symbol"]:
                    if len(word)<4:
                        continue
                    list_renamed.append(word)
        full_name_tokenized = []
        fullname2symbol = {}
        fullname = []
        for name in list_renamed:
            name = text_normalize(name)
            tks = []
            for t in self.nlp(name):
                tks.append(t.text.lower)
            if tks not in full_name_tokenized:
                full_name_tokenized.append(tks)
                fullname2symbol[name.lower()] = info["symbol"]
                fullname.append(name)
        return fullname2symbol, fullname

    def update_derivative_symbols(self, derivative_symbols):
        try:
            list_derivative_symbols = []
            list_derivative_symbolTypes = []
            list_derivative_underlyingSymbols = []
            self.symbolType2Symbol = {}
            self.underlyingSymbol2Symbol = {}
            for (symbol, symbolType, underlyingSymbol) in derivative_symbols:
                if symbol not in list_derivative_symbols:
                    list_derivative_symbols.append(symbol)

                if symbolType not in list_derivative_symbolTypes:
                    list_derivative_symbolTypes.append(symbolType)

                if underlyingSymbol not in list_derivative_underlyingSymbols:
                    list_derivative_underlyingSymbols.append(underlyingSymbol)

                self.symbolType2Symbol[symbolType] = symbol
                if underlyingSymbol not in self.underlyingSymbol2Symbol:
                    self.underlyingSymbol2Symbol[underlyingSymbol] = []
                if symbol not in self.underlyingSymbol2Symbol[underlyingSymbol]:
                    self.underlyingSymbol2Symbol[underlyingSymbol].append(symbol)
            self.derivative_symbol_patterns = [{"LOWER": {"IN": [sym.lower() for sym in list_derivative_symbols]}}]
            self.derivative_symbolType_patterns = [{"LOWER": {"IN": [sym.lower() for sym in list_derivative_symbolTypes]}}]
            self.derivative_underlyingSymbol_patterns = [{"LOWER": {"IN": [sym.lower() for sym in list_derivative_underlyingSymbols]}}]
        except Exception as e:
            raise e
        
    # detect via symbols
    def detect_symbol(self, doc, doc_vietnamese):
        symbols_detected = []
        # check symbol
        symbol_matcher = Matcher(self.nlp_vietnamese.vocab)
        # symbol_matcher = Matcher(self.nlp.vocab)
        symbol_matcher.add("symbol", [self.symbol_patterns])
        results = symbol_matcher(doc_vietnamese)
        ambiguos_symbols = []
        for (match_id, start, end) in results:
            symbol = doc_vietnamese[start].text
            tag = doc_vietnamese[start].tag_
            pos = doc_vietnamese[start].dep_
            pre_token = None
            symbol = symbol.upper()
            is_symbol = True
            try:
                pre_token = doc_vietnamese[start-1].text
            except:
                pass
            if pre_token is not None:
                if pre_token in PRE_TOKEN:
                    symbols_detected.append(symbol)
                    continue
                else:
                    if 'N' not in tag or symbol in FAILURE_SYMBOLS:
                        is_symbol = False
            else:
                if symbol in FAILURE_SYMBOLS:
                    is_symbol = False

            # check symbols
            if symbol in self.symbolinname:
                for csymbol, tokenized_name in self.symbolinname[symbol]:
                    try:
                        pre_token = doc_vietnamese[start-1]
                        if pre_token in tokenized_name:
                            is_symbol = False
                    except:
                        pass

                    try:
                        sub_token = doc_vietnamese[start+1]
                        if sub_token in tokenized_name:
                            is_symbol = False
                    except:
                        pass
            # if is_symbol and symbol not in symbols_detected:
            if is_symbol:
                symbols_detected.append(symbol)
            else:
                ambiguos_symbols.append(symbol)
        # print(symbols_detected)
        ## re check ambiguos
        if len(symbols_detected) == 0:
            if len(ambiguos_symbols)==1 and ambiguos_symbols[0] not in FAILURE_SYMBOLS:
                symbols_detected.append(ambiguos_symbols[0])
            else:
                for sym in ambiguos_symbols:
                    if sym not in FAILURE_SYMBOLS:
                        symbols_detected.append(sym)
        else:
            for sym in ambiguos_symbols:
                if sym not in FAILURE_SYMBOLS:
                    symbols_detected.append(sym)
        # print(symbols_detected)
        # processing with English
        if len(symbols_detected) == 0:
            symbols_detected = []
            # check symbol
            symbol_matcher = Matcher(self.nlp.vocab)
            # symbol_matcher = Matcher(self.nlp.vocab)
            symbol_matcher.add("symbol", [self.symbol_patterns])
            results = symbol_matcher(doc)
            ambiguos_symbols = []
            for (match_id, start, end) in results:
                symbol = doc[start].text
                tag = doc[start].tag_
                pos = doc[start].dep_
                pre_token = None
                symbol = symbol.upper()
                is_symbol = True
                try:
                    pre_token = doc[start-1].text
                except:
                    pass
                if pre_token is not None:
                    if pre_token in PRE_TOKEN:
                        symbols_detected.append(symbol)
                        continue
                    else:
                        if 'N' not in tag or symbol in FAILURE_SYMBOLS:
                            is_symbol = False
                else:
                    if symbol in FAILURE_SYMBOLS:
                        is_symbol = False

                # check symbols
                if symbol in self.symbolinname:
                    for csymbol, tokenized_name in self.symbolinname[symbol]:
                        try:
                            pre_token = doc[start-1]
                            if pre_token in tokenized_name:
                                is_symbol = False
                        except:
                            pass

                        try:
                            sub_token = doc[start+1]
                            if sub_token in tokenized_name:
                                is_symbol = False
                        except:
                            pass
                # if is_symbol and symbol not in symbols_detected:
                if is_symbol:
                    symbols_detected.append(symbol)
                else:
                    ambiguos_symbols.append(symbol)
            ## re check ambiguos
            if len(symbols_detected) == 0:
                if len(ambiguos_symbols)==1 and ambiguos_symbols[0] not in FAILURE_SYMBOLS:
                    symbols_detected.append(ambiguos_symbols[0])
                else:
                    for sym in ambiguos_symbols:
                        if sym not in FAILURE_SYMBOLS:
                            symbols_detected.append(sym)
            else:
                for sym in ambiguos_symbols:
                    if sym not in FAILURE_SYMBOLS:
                        symbols_detected.append(sym)

            #  re-order symbol
            reordered_symbol = []
            last_order_symbol = []
            for sym in symbols_detected:
                if sym in LAST_ORDER_SYMBOLS:
                    last_order_symbol = [sym] + last_order_symbol
                else:
                    reordered_symbol.append(sym)
            return reordered_symbol + last_order_symbol
        else:
            #  re-order symbol
            reordered_symbol = []
            last_order_symbol = []
            for sym in symbols_detected:
                if sym in LAST_ORDER_SYMBOLS:
                    last_order_symbol = [sym] + last_order_symbol
                else:
                    reordered_symbol.append(sym)
            return reordered_symbol + last_order_symbol

    # detect via derivative symbols
    def detect_derivative_symbol(self, doc):
        derivative_symbols_detected = []

        # check symbol
        symbol_matcher = Matcher(self.nlp.vocab)
        symbol_matcher.add("symbol", [self.derivative_symbol_patterns])
        symbol_matcher.add("symbolType", [self.derivative_symbolType_patterns])
        # symbol_matcher.add("underlyingSymbol", [self.derivative_underlyingSymbol_patterns])
        results = symbol_matcher(doc)
        for (match_id, start, end) in results:
            matching_type = doc.vocab.strings[match_id]
            symbol = doc[start:end].text
            if matching_type == 'symbol':
                derivative_symbols_detected.append(symbol.upper())

            
            if matching_type == 'symbolType':
                derivative_symbols_detected.append(self.symbolType2Symbol[symbol.upper()])

            # if matching_type == 'underlyingSymbol':
            #     is_correct = True
            #     try:
            #         pre_token = doc[start-1].text
            #         if pre_token[0].isupper():
            #             is_correct=False
            #         if pre_token =='Chỉ số':
            #             is_correct=True
            #     except:
            #         pass
            #     if is_correct:
            #         derivative_symbols_detected += self.underlyingSymbol2Symbol[symbol]

        return derivative_symbols_detected

    # detect via name of company
    def detect_names(self, doc):
        symbol_detected = []
        # check name
        name_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        name_matcher.add("fullname", self.full_name_patterns)

        start2symbol = {}
        results = name_matcher(doc)
        for match_id, start, end in results:
            # get name of company
            try:
                name_detected = doc[start:end].text.lower()
                name_detected = name_detected.replace('-', ' - ')
                name_detected = name_detected.replace('(', ' ( ')
                name_detected = name_detected.replace(')', ' ) ')
                name_detected = re.sub(' +',' ', name_detected).strip()
                symbol = self.fullname2symbol[name_detected]
            except Exception as e:
                continue
            
            if start not in start2symbol:
                start2symbol[start] = {'symbol': symbol, 'start': start, 'end': end}
            else:
                prev_end = start2symbol[start]['end']
                if end>prev_end:
                    start2symbol[start]['end'] = end
                    start2symbol[start]['symbol'] = symbol

        end2symbol = {}
        for start in start2symbol:
            symbol = start2symbol[start]["symbol"]
            end = start2symbol[start]["end"]
            start = start2symbol[start]["start"]
            if end not in end2symbol:
                end2symbol[end] = start2symbol[start]
            else:
                prev_start = end2symbol[end]["start"]
                if start < prev_start:
                    end2symbol[end]['start'] = start
                    end2symbol[end]['symbol'] = symbol
        for end in end2symbol:
            symbol = end2symbol[end]['symbol']
            symbol_detected.append(symbol)

        return symbol_detected
    
    def detect(self, content, derivative_mapping=True):  # --> list symbols are mentioned in the new

        if self.curr_created_date is None:
            import time
            t = time.time()
            self.update_data()
            # call api 
            try:
                # print("update derivative symbols")
                derivative_json_data = None
                derivative_json_data = requests.get('https://api.dnse.com.vn/chart-api/symbols?type=derivativemapping').json()
                derivative_data = []
                for item in derivative_json_data['mapping']:
                    self.derivative_mapping_data[item['symbol']] = item['symbolType']
                    derivative_data.append((item['symbol'], item['symbolType'], "VN30"))
                # print(derivative_data)
                
                for item_symbol in ['VN30F1M', 'VN30F2M', 'VN30F1Q', 'VN30F2Q']:
                    self.derivative_mapping_data[item_symbol] = item_symbol
                    derivative_data.append((item_symbol, item_symbol, "VN30"))
                self.update_derivative_symbols(derivative_data)
            except:
                pass
            print(time.time()-t)
        assert self.curr_created_date is not None, "Invalid symbol data file or format"

        if (datetime.datetime.now() > self.curr_created_date + datetime.timedelta(days=self.num_date_expire)) and not self.is_updating:
            self.is_updating = True
            # print("update derivative symbols")
            self.update_data()
            # call api 
            try:
                derivative_json_data = None
                derivative_json_data = requests.get('https://api.dnse.com.vn/chart-api/symbols?type=derivativemapping').json()
                derivative_data = []
                for item in derivative_json_data['mapping']:
                    self.derivative_mapping_data[item['symbol']] = item['symbolType']
                    derivative_data.append((item['symbol'], item['symbolType'], "VN30"))
                # print(derivative_data)
                
                for item_symbol in ['VN30F1M', 'VN30F2M', 'VN30F1Q', 'VN30F2Q']:
                    self.derivative_mapping_data[item_symbol] = item_symbol
                    derivative_data.append((item_symbol, item_symbol, "VN30"))
                self.update_derivative_symbols(derivative_data)
            except:
                pass

        content = text_normalize(content)
        final_symbols_detected = {}
        symbols_detected_via_symbols = []
        symbols_detected_via_names = []

        try:
            doc = self.nlp(content)
            doc_vietnamese = self.nlp_vietnamese(content)
        except:
            logging.info("New content is unvalid (too short, etc)")
            return final_symbols_detected

        # if confirm patern existed
        symbols_detected_via_names = self.detect_names(doc)
        symbols_detected_via_symbols = self.detect_symbol(doc, doc_vietnamese)
        detect_derivative_symbols_raw = self.detect_derivative_symbol(doc)
        
        for d_symbol in ['vn30f1m', 'vn30f2m', 'vn30f1q', 'vn30f2q']:
            if d_symbol in content.lower():
                detect_derivative_symbols_raw.append(d_symbol.upper())

        detect_derivative_symbols = []
        if derivative_mapping:
            try:
                for symbol in detect_derivative_symbols_raw:
                    detect_derivative_symbols.append(self.derivative_mapping_data[str(symbol).upper()])
            except Exception as e:
                detect_derivative_symbols = detect_derivative_symbols_raw
        # combine both symbols detected type (detected via symbols and detected via name of company)

        for symbol in detect_derivative_symbols:
            if symbol not in final_symbols_detected:  # get unique list symbols
                final_symbols_detected[symbol] = 0
            final_symbols_detected[symbol] += 1
        
        for symbol in symbols_detected_via_names:
            if symbol not in final_symbols_detected:  # get unique list symbols
                final_symbols_detected[symbol] = 0
            final_symbols_detected[symbol] += 1

        # detect symbol via symbol
        translated_symbol = []
        for symbol in symbols_detected_via_symbols:
            is_symbol = True
            if symbol in self.symbolinname2symbols:
                for true_symbol in self.symbolinname2symbols[symbol]:
                    if true_symbol in symbols_detected_via_names:
                        translated_symbol.append(true_symbol)
                        is_symbol = False
                        break
            if is_symbol:
                translated_symbol.append(symbol)
        
        for symbol in translated_symbol:
            if symbol not in final_symbols_detected:  # get unique list symbols
                final_symbols_detected[symbol] = 0
            try:
                final_symbols_detected[symbol] += 1
            except:
                pass
        return final_symbols_detected


# if __name__=='__main__':
#     d = QuestionSymbolDetector()
#     print(d.detect('ai là CEO của VNM'))
#     print(d.detect('hpg hôm nay có gì không'))
#     print(d.detect('hôm nay có tin gì về hpg ko'))
#     print(d.detect('hpg vs vic có tin gì không'))
#     print(d.detect('HPG vs VIC có tin gì không'))
#     print(d.detect('CEO có tin gì không'))
#     print(d.detect('có tin gì về hpg vs vic không'))
#     print(d.detect('mã tin'))
#     print(d.detect('mã hai'))
#     print(d.detect('mã tin có tin gì ko'))
#     print(d.detect('mã vat'))

#     lower_symbol = [s.lower() for s in d.symbols]
#     vocab = set(d.nlp_vietnamese.vocab.strings)
#     print('Vocab size: ', len(vocab))
#     print('Num symbols: ', len(lower_symbol))
#     valid_vocab = 0
#     for w in lower_symbol:
#         if w in vocab:
#             valid_vocab +=1 
#     print('Total existed token: ', valid_vocab)