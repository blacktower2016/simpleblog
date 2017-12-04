from django.test import LiveServerTestCase
from selenium import webdriver
from django.urls import reverse
from django.utils.translation import activate, gettext_lazy as _
from .creation_utils import create_user
from simpleblog.models import Post

class TestSignup(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.user = create_user()
        #activate("en")

    def test_log_in_and_create_new_post(self):
        # user come to the simpleblog to create post
        self.driver.get(self.live_server_url+reverse("simpleblog:create-post"))

        self.assertIn("<h2>Вход</h2>", self.driver.page_source)

        # Oh, I forgot to log in!

        self.driver.find_element_by_id("id_username").send_keys("user")
        self.driver.find_element_by_id("id_password").send_keys("password")
        self.driver.find_element_by_tag_name('button').click()

        self.assertIn("user", self.driver.page_source)

        # create post
        self.driver.find_element_by_partial_link_text("Новая").click()
        self.assertIn("Новая запись", self.driver.page_source)

        self.driver.find_element_by_id("id_title").send_keys("New post title")
        self.driver.find_element_by_id("id_subtitle").send_keys("New post subtitle")
        self.driver.find_element_by_id("id_text").send_keys("New post text")
        self.driver.find_element_by_id("id_tags").send_keys("New post tag")
        self.driver.find_element_by_tag_name('button').click()

        self.assertEqual(Post.objects.count(), 1)

    def tearDown(self):
        #self.driver.quit()
        pass

if __name__ == '__main__':
    unittest.main()
