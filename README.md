This is the code I use to creat a ncusip (historical cusip) - cik (historical cik) mapping. 

# why I need this?
A referee from Journal of Baning and Finance asks us to incorproate historical headquarters location data. Note that Compustat only provides CURRENT CUSIPs, current CIKs, and current headquarters.

# Where are alternatives?
1. WRDS has a (historical) CIK-CUSIP (or even GVKEY-CIK) link table. But business schools (at least in the UK) seldom subscribe it.
2. This code is inspired by Leo Liu's CIK-CUSIP mapping. I also borrow some codes from him. Thanks. https://github.com/leoliu0/cik-cusip-mapping
   You can also find a csv. file at Liu's webpage. But date stamps are moved, which make the mapping not enough for me.
3. There is a paper studing this and create a to make a mapping. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3530613 But I did not find there code or mapping file. It is still good to know more about this issue.

# So what is the issue on earth?
1. Compustat only provides CURRENT CUSIPs, current CIKs, and current headquarters
2. Historical headquarters data is avaiable here, however, CIK (historical CIK) is the only identifier. https://sraf.nd.edu/sec-edgar-data/10-x-header-data/
3. Therefore, the requirement is build a link from Compustat GVKEY/CUSIP (Current CUSIP) to historical CUSIP (e.g., CRSP NCUSIP) to historical CIK to historical HQ locations
4. ( WRDS has a (historical) CIK-CUSIP (or even GVKEY-CIK) link table)
5. Manually, we can use 13D and 13G reportings to collect the mapping. As this is also how WRDS creates the mapping. WRDS: "This web query provides the historical link between a company's CIK and GVKEY. We create this link by first getting the CUSIP from a company's Schedule 13D/G. We then use the CUSIP to link the CIK from the header of the Schedule 13D/G to GVKEY in the Compustat tables."

# The function of this code
1. Get all discloasures from SEC Edgar. => "Download_SEC_File_List_CIK.py"
2. Select only 13D and 13G files. => "Download_SEC_13D13G_CUSIP-CIK_Mapping.py"
3. Use regular expression (RE) to obtain the CUSIP and CIK for each 13D/13G. This is a pair and all pairs make a mapping. => "Download_SEC_13D13G_CUSIP-CIK_Mapping.py"

# Some issues about this code
1. The code costs time very much.

   1.1 I try to only use the first 200 lines of each report and remove all 13D/A and 13G/A (additional files)
   
   1.2 It still take me more than 10 hours to run it locally, with two laptops (one M2 chip Macbook pro and one 16G memory AMD R9 Win)
   
2. I see some missing values there, but it is not a big issue for me meanwhile. I will fix this later on.
3. The code is difficult to deploy on server.
   
   3.1 I tried to deploy it on AWS EC2 but failed every way. It seems EDGAR will detect this and ban the scraping. I will try to fix this later on.

4. When using the mapping, it is notable that the date is not continuous, as these dates are only when 13D or 13G is published. So filling up is necessary.
