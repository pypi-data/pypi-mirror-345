import os
import spacy
from spacy.lang.vi import Vietnamese
import json
import numpy as np
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
import logging
import re
import datetime
from .init_data import JSON_DATA_STR, ADDITIONAL_DATA_SYMBOLS

FAILURE_SYMBOLS = ["MTV", "USD", "CEO", "HCM", "TIP", "APP", "AMD", "CAR", "CLG", "DNA", "FOX", "SBS", 'PGD', 'CNN', 'SJC', 'BOT', 'PPP', 'AAA', 'VND', 'CPI', 'CMC', 'NAV', 'API', 'TOP']

class SymbolDetector:
    def __init__(self):
        self.symbol2info = {}
        self.symbols = []
        self.fullname2symbol = {}
        self.additionalsymbol2name = {}
        self.symbolinname = {}
        self.symbolinname2symbols = {}
        self.fullname = []
        self.nlp = Vietnamese()

        self.curr_created_date = None
        self.is_updating = False
        try:
            self.get_info()
        except Exception as e:
            raise e

        self.symbol_patterns = [{"TEXT": {"IN": self.symbols}}]
        self.full_name_patterns = [
            self.nlp.make_doc(name) for name in list(self.fullname)
        ]
        self.confirm_patterns = [{"LOWER": {"IN": ["cổ phiếu", "chứng khoán"]}}]

    def get_info(self):
        
        for comp in ADDITIONAL_DATA_SYMBOLS:
            symbol = comp['symbol']
            name = comp['name']
            if symbol not in self.additionalsymbol2name:
                self.additionalsymbol2name[symbol] = []
            self.additionalsymbol2name[symbol].append(name)

        # get infor to detect symbol
        JSON_DATA = json.loads(JSON_DATA_STR)
        self.curr_created_date = datetime.datetime.strptime(JSON_DATA['created_date'], '%Y-%m-%d')
        for comp in JSON_DATA['data']:
            if len(comp["symbol"].strip()) != 3:
                continue
            info = {
                "symbol": comp["symbol"],
                "name": comp["name"],
                "full_name": comp["companyName"],
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
            self.derivative_symbol_patterns = [{"TEXT": {"IN": list_derivative_symbols}}]
            self.derivative_symbolType_patterns = [{"TEXT": {"IN": list_derivative_symbolTypes}}]
            self.derivative_underlyingSymbol_patterns = [{"TEXT": {"IN": list_derivative_underlyingSymbols}}]
        except Exception as e:
            raise e
        
    def update_data(self, symbol_data):
        try:
            self.additionalsymbol2name = {}
            symbols = []
            symbol2info = {}
            fullname = []
            fullname2symbol = {}
            symbolinname = {}
            symbolinname2symbols = {}
            for comp in ADDITIONAL_DATA_SYMBOLS:
                symbol = comp['symbol']
                name = comp['name']
                if symbol not in self.additionalsymbol2name:
                    self.additionalsymbol2name[symbol] = []
                self.additionalsymbol2name[symbol].append(name)
            # get infor to detect symbol
            for comp in symbol_data:
                if len(comp["symbol"].strip()) != 3:
                    continue
                info = {
                    "symbol": comp["symbol"],
                    "name": comp["name"],
                    "full_name": comp["companyName"],
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
            self.symbol_patterns = [{"TEXT": {"IN": self.symbols}}]
            self.full_name_patterns = [
                self.nlp.make_doc(name) for name in list(self.fullname)
            ]

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
            if info["symbol"]  not in ['HCM']:
                list_renamed.append(full_name.replace("CTCP ", "").strip())
            list_renamed.append(full_name.replace("CTCP Chứng khoán", "CTCK").strip())
            
        if info["symbol"] in self.additionalsymbol2name:
            for name in self.additionalsymbol2name[info["symbol"]]:
                list_renamed.append(name)


        full_name_tokenized = []
        fullname2symbol = {}
        fullname = []
        for name in list_renamed:
            tks = []
            for t in self.nlp(name):
                tks.append(t.text.lower)
            if tks not in full_name_tokenized:
                full_name_tokenized.append(tks)
                fullname2symbol[name.lower()] = info["symbol"]
                fullname.append(name)
        return fullname2symbol, fullname

    def check_confirm_pattern(self, doc):
        # double check, it is confirmed by some special characters
        confirm_matcher = Matcher(self.nlp.vocab)
        confirm_matcher.add("check", [self.confirm_patterns])
        results = confirm_matcher(doc)

        if len(results) > 0:  # if confirm patterns existed
            return True
        return False

    # detect via symbols
    def detect_symbol(self, doc):
        symbols_detected = []

        # check symbol
        symbol_matcher = Matcher(self.nlp.vocab)
        symbol_matcher.add("symbol", [self.symbol_patterns])
        results = symbol_matcher(doc)
        for (match_id, start, end) in results:
            symbol = doc[start:end].text
            # check failure symbols 
            is_symbol = False
            if symbol in FAILURE_SYMBOLS:
                for sk in ["cổ phiếu", "cp", 'mã']:
                    if sk in doc[(start-2):start].text.lower():
                        is_symbol = True
                        break
            else:
                try:
                    sub_token = doc[start+1].text
                    if sub_token[0].isupper():
                        is_symbol = False
                    elif sub_token.isnumeric():
                        is_symbol = False
                    else:
                        is_symbol = True
                except Exception as e:
                    is_symbol = True
            if symbol in self.symbolinname:
                for csymbol, tokenized_name in self.symbolinname[symbol]:
                    try:
                        pre_token = doc[start-1].text
                        if pre_token in tokenized_name:
                            is_symbol = False
                    except Exception as e:
                        logging.info(f'DET ERROR: {e}')
                        pass

                    try:
                        sub_token = doc[start+1].text
                        if sub_token in tokenized_name:
                            is_symbol = False
                    except Exception as e:
                        logging.info(f'DET ERROR: {e}')
                        pass
            # if is_symbol and symbol not in symbols_detected:
            if is_symbol:
                symbols_detected.append(symbol)

        return symbols_detected

    # detect via derivative symbols
    def detect_derivative_symbol(self, doc):
        derivative_symbols_detected = []

        # check symbol
        symbol_matcher = Matcher(self.nlp.vocab)
        symbol_matcher.add("symbol", [self.derivative_symbol_patterns])
        symbol_matcher.add("symbolType", [self.derivative_symbolType_patterns])
        symbol_matcher.add("underlyingSymbol", [self.derivative_underlyingSymbol_patterns])
        results = symbol_matcher(doc)
        for (match_id, start, end) in results:
            matching_type = doc.vocab.strings[match_id]
            symbol = doc[start:end].text
            if matching_type == 'symbol':
                derivative_symbols_detected.append(symbol)
            
            if matching_type == 'symbolType':
                derivative_symbols_detected.append(self.symbolType2Symbol[symbol])

            if matching_type == 'underlyingSymbol':
                is_correct = True
                try:
                    pre_token = doc[start-1].text
                    if pre_token[0].isupper():
                        is_correct=False
                    if pre_token =='Chỉ số':
                        is_correct=True
                except:
                    pass
                if is_correct:
                    derivative_symbols_detected += self.underlyingSymbol2Symbol[symbol]

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

        for start in start2symbol:
            symbol = start2symbol[start]["symbol"]
            # if symbol not in symbol_detected:
            symbol_detected.append(symbol)

        return symbol_detected
    
    def detect(self, content):  # --> list symbols are mentioned in the new
        final_symbols_detected = {}
        symbols_detected_via_symbols = []
        symbols_detected_via_names = []

        try:
            doc = self.nlp(content)
        except:
            logging.info("New content is unvalid (too short, etc)")
            return final_symbols_detected

        # if confirm patern existed
        symbols_detected_via_names = self.detect_names(doc)

        is_confirm =  self.check_confirm_pattern(doc)
        symbols_detected_via_symbols = self.detect_symbol(doc)

        # combine both symbols detected type (detected via symbols and detected via name of company)
        for symbol in symbols_detected_via_names:
            if symbol not in final_symbols_detected:  # get unique list symbols
                final_symbols_detected[symbol] = 0
            final_symbols_detected[symbol] += 1

        # detect derivative symbol
        detected_derivative_symbol = self.detect_derivative_symbol(doc)
        for symbol in detected_derivative_symbol:
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
            if symbol not in final_symbols_detected and is_confirm:  # get unique list symbols
                final_symbols_detected[symbol] = 0
            try:
                final_symbols_detected[symbol] += 1
            except:
                pass
        filter_symbols_detected = {}
        if 'VIC' in final_symbols_detected and 'VFS' in final_symbols_detected:
            for k in final_symbols_detected:
                if k != 'VFS':
                    filter_symbols_detected[k] = final_symbols_detected[k]
            return filter_symbols_detected
        else:
            return final_symbols_detected

    def detect_wo_confirm(self, content):  # --> list symbols are mentioned in the new
        final_symbols_detected = {}
        symbols_detected_via_symbols = []
        symbols_detected_via_names = []

        try:
            doc = self.nlp(content)
        except:
            logging.info("New content is unvalid (too short, etc)")
            return final_symbols_detected

        # if confirm patern existed
        symbols_detected_via_names = self.detect_names(doc)
        # print('Name: ',symbols_detected_via_names)
        symbols_detected_via_symbols = self.detect_symbol(doc)
        # print('Symbols: ',symbols_detected_via_symbols)
        # combine both symbols detected type (detected via symbols and detected via name of company)
        for symbol in symbols_detected_via_names:
            if symbol not in final_symbols_detected:  # get unique list symbols
                final_symbols_detected[symbol] = 0
            final_symbols_detected[symbol] += 1

        # detect derivative symbol
        detected_derivative_symbol = self.detect_derivative_symbol(doc)
        for symbol in detected_derivative_symbol:
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
        
        filter_symbols_detected = {}
        if 'VIC' in final_symbols_detected and 'VFS' in final_symbols_detected:
            for k in final_symbols_detected:
                if k != 'VFS':
                    filter_symbols_detected[k] = final_symbols_detected[k]
            return filter_symbols_detected
        else:
            return final_symbols_detected