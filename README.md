**InstagramSpider**
Complete parsing of followers and following by given user list:
        1. Followers list
        2. Followings list
        3. Username
        4. User ID
        5. For every follower and followings user parsing photo link
        6. Is private

**Book24Spider**
Searching books by gived keyword and parse book data:
        1. Book link
        2. Book title
        3. Authors
        4. Main price
        5. Price with discount
        6. Book rate

**LeruaSpider**
Searching items by given keyword and parse items data:
        1. Title
        2. Item characteristics
        3. Item price
        4. Item link
        4. Item photos, saving in folders named by item title

**HH_parser.py**
Complete hh.ru vacancies parsing by given keyword:
        1. Vacancy title
        2. Salary range
        3. Vacancy link
        4. Currency
        5. Saving parsed data via:
            a. CSV
            b. JSON
            c. MongoDB instanse (uppend mode included)
        6. Complete searching by saved results in MongoDB
        
**News_parser.py**
Complete lenta.ru/yandex.news.ru/news.mail.ru parsing:
        1. News title
        2. Publication date
        3. Link
        4. Source
        5. Source link
        6. Saving parsed data in MongoDB
        
**Vk_parser_selenium.py**
Complete parsing of posts in vk.com communities by given keyword without login:
        1. Post data
        2. Post text
        3. Post link
        4. Post attachments links (if included)
        5. Likes/Shares/Views of post
        6. Saving parsed data in MongoDB
        7. Wall scrolling till the enв
        8. Skip login banner
        
