package LoadTesting;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;


public class PageLoad {

    public static void main(String[] args) throws InterruptedException {
        
        //create firefox driver object
        //WebDriver driver = new FirefoxDriver();
        
        //create chrome driver object
        System.setProperty("webdriver.chrome.driver", "/Users/runy1/Downloads/chromedriver");
        WebDriver driver = new ChromeDriver();
        driver.get("http://www.wikipedia.org");
        
        //find the link
        WebElement link;
        link = driver.findElement(By.linkText("English"));
        link.click();
        Thread.sleep(5000);
        
        //find searchBox
        WebElement searchBox;
        searchBox = driver.findElement(By.id("searchInput"));
        searchBox.sendKeys("Software");
        searchBox.submit();
        Thread.sleep(5000);
        
        //close browser
        driver.quit();
        
    }

}
