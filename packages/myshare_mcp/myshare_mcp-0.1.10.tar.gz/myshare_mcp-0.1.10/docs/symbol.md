## Symbol

Please implement a function which accept a symbol (in format in the below table or a symbol without suffix) and return the symbol and a market suffix. Please refer to the below requirements.

We need to handle symbol defined in the following table and we should be able to handle the symbol in the original format as well. This means that regardless of how the symbol is presented initially, our system should be capable of processing it without issues.

Ideally, if we want to process a symbol from Shanghai market, the symbol format 6xxxxx.SH should be used. This is the standard and preferred format for representing Shanghai market symbols. However, we should also be able to handle the abbreviated form 6xxxxx. This flexibility is important as users may input the symbol in different ways. For instance, when referring to 大秦铁路，the user can input either 601006.SH or 601006, and our system should correctly identify and process it as the symbol for 大秦铁路. This dual - format handling ensures a better user experience and reduces the chance of input errors causing processing failures.

The following table is the format of stock symbol for different markets.

| Market    | Market Suffix | Format    | Remarks                     |
| --------- | ------------- | --------- | --------------------------- |
| Shanghai  | SH            | 6xxxxx.SH | 601006.SH (大秦铁路)            |
| Shenzhen  | SZ            | 000002.SZ | 000002.SZ (万科A) 主板          |
| Shenzhen  | SZ            | 300002.SZ | 300750.SZ (宁德时代) 创业板        |
| Hong Kong | HKI           | 0700.HK   | 0700.HK (腾讯控股)              |
| Singapore | SI            | xxx.SI    | C6L.SI (Singapore Airlines) |
| US        | US            | xxxx      | EPAM                        |

---

中国股票代码的命名规则主要由交易所和板块决定，不同市场和板块的代码前缀不同。以下是主要规则和分类：

---

​**​一、上海证券交易所（沪市）​**​

1. 主板（A股）  
   • 代码范围：600、601、603、605 开头
   
   • 示例：
   
   ◦ 中国平安（601318）
   
   ◦ 大秦铁路（601006）

2. 科创板（科技创新企业）  
   • 代码范围：688 开头
   
   • 示例：中芯国际（688981）

3. B股（外资股）  
   • 代码范围：900 开头
   
   • 示例：老凤祥B（900905）

---

​**​二、深圳证券交易所（深市）​**​

1. 主板（A股）  
   • 代码范围：000、001、002、003 开头
   
   ◦ 000 和 001 是原主板代码（如平安银行 000001）
   
   ◦ 002 和 003 是原中小板代码（合并后沿用）
   
   • 示例：万科A（000002）

2. 创业板（成长型企业）  
   • 代码范围：300 开头
   
   • 示例：宁德时代（300750）

3. B股（外资股）  
   • 代码范围：200 开头
   
   • 示例：深南电B（200037）

---

​**​三、北京证券交易所（北交所）​**​  
• 代码范围：43、83、87、88、92、93 开头

• 示例：贝特瑞（835185），万达轴承（920002）

---

​**​四、其他特殊代码​**​

1. 新股申购代码  
   • 沪市：730、732 开头
   
   • 深市：与股票代码一致（如创业板新股代码仍为300开头）。

2. 配股代码  
   • 沪市：700 开头（如中国平安配股代码 700318）
   
   • 深市：080 开头（如平安银行配股代码 080001）。

3. 退市整理板  
   • 沪市：600 开头
   
   • 深市：300 开头。

---

​**​五、代码命名特点​**​

1. 顺序编码：同一板块内按上市顺序分配代码，如平安银行（000001）是深市最早的股票。
2. 无行业或地区标识：中国股票代码不包含行业或地区信息，仅反映市场和板块。
3. B股特殊标识：沪市B股以900开头，深市B股以200开头，与A股区分。

---

​**​总结示例​**​  
• 平安银行（000001）：深市主板，代码000开头。

• 大秦铁路（601006）：沪市主板，代码601开头。

• 宁德时代（300750）：深市创业板，代码300开头。

• 中芯国际（688981）：沪市科创板，代码688开头。

通过代码前缀，可以快速判断股票所属市场和板块，这对投资者分析公司属性和交易规则具有重要意义。
