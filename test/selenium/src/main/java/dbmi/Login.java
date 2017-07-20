package dbmi;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.*;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.remote.RemoteWebDriver;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.interactions.Action;
import org.openqa.selenium.Dimension;

import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.Keys;

import java.util.List;

/**
 *@author: Yifan Ning
 *@date: Dec 13, 2016 5:01:32 PM
 *
 */
public class Login extends TestBase{

    @Test
    public void test_user_login() throws InterruptedException {        
        driver.get(appUrl);
        driver.manage().window().maximize();
        Thread.sleep(800);
        driver.findElement(By.linkText("Login")).click(); // click login 
        Thread.sleep(500);
        driver.findElement(By.name("email")).sendKeys("test@gmail.com"); // fill username
        driver.findElement(By.name("password")).sendKeys("testtest"); // fill password
        Thread.sleep(500);
        driver.findElement(By.xpath("//button[contains(.,'Login')]")).click(); // submit 
        Thread.sleep(1000);
        // driver.findElement(By.linkText("Logout")).click(); // logout

        // load test PMC article
        driver.findElement(By.name("sourceURL")).sendKeys("http://localhost/PMC/PMC2686069.html");
        // driver.findElement(By.name("sourceURL")).sendKeys("http://localhost/test/test.html");
        driver.findElement(By.xpath("//button[contains(.,'load')]")).click();
        Thread.sleep(1500);

        // import existing annotations
        driver.findElement(By.xpath("//button[contains(.,'Import')]")).click(); // import
        Thread.sleep(1500);

        /*
        ANNOTATE ARTICLE
        */

        // WebElement firstP = driver.findElement(By.id("drug1")); // for test file
        WebElement firstP = driver.findElement(By.id("__p14"));

        // create drug mention 1
        createDrug(firstP,0,0);

        //move cursor to a new word, create drug mention 2
        createDrug(firstP,100,150);

        // highlight passage until beginning of following paragraph
        WebElement next = driver.findElement(By.id("__p15"));
        Actions highlight = new Actions(driver);
        System.out.println(firstP + "\n" + next);
        highlight.moveToElement(firstP,0,0).click();
        highlight.keyDown(Keys.SHIFT);
        highlight.moveToElement(next,0,0).click();
        highlight.keyUp(Keys.SHIFT);
        highlight.build().perform();
        Thread.sleep(2000);

        // create claim with the highlighted passage
        WebElement mp = driver.findElement(By.className("mp-menu-btn"));
        Actions claim = new Actions(driver);
        claim.moveToElement(mp).build().perform();
        driver.findElement(By.className("mp-main-menu-1")).click();
        Thread.sleep(2000);

        WebElement d1 =  driver.findElement(By.id("Drug1"));
        Select dropdown1 = new Select(d1);
        // dropdown1.selectByVisibleText("warfarin");
        dropdown1.selectByIndex(1);
        Thread.sleep(1000);

        WebElement d2 = driver.findElement(By.id("Drug2"));
        Select dropdown2 = new Select(d2);
        // dropdown2.selectByVisibleText("ambrisentan");
        dropdown2.selectByIndex(2);
        Thread.sleep(1000);

        WebElement precipitant = driver.findElement(By.id("drug1precipitant"));
        precipitant.click();
        Thread.sleep(2000);

        driver.findElement(By.xpath("//button[contains(.,'Save and Close')]")).click();
        Thread.sleep(2000);

        driver.findElement(By.id("finish-same-span-btn")).click();
        Thread.sleep(2000);

        // edit drug claim - check dropdown menus for "Relationships" and "Methods"
        // driver.findElement(By.className("btn btn-success")).click();
        driver.findElement(By.xpath("//button[contains(.,'Edit Claim')]")).click();
        Thread.sleep(1500);

        WebElement methods = driver.findElement(By.id("method"));
        Select dropdownM = new Select(methods);
        List<WebElement> dd = dropdownM.getOptions();

        //Get length
        System.out.println(dd.size() + " methods options");

        // Loop to print one by one
        for (int i = 0; i < dd.size(); i++) {
            System.out.println("METHOD INDEX " + i + ": " + dd.get(i).getText());
            dropdownM.selectByIndex(i);
            Thread.sleep(2000);

            // inner loop for the new sets of relationships that come up for each method.
            WebElement relationships = driver.findElement(By.id("relationship"));
            Select dropdownR = new Select(relationships);
            List<WebElement> de = dropdownR.getOptions();

            for(int j = 0; j < de.size(); j++) {
                // System.out.println(de.get(j).getAttribute("disabled"));
                if (de.get(j).getAttribute("disabled") == null) {
                    System.out.println("RELATIONSHIP INDEX " + j + ": " + de.get(j).getText());
                }
            }
        }

        // delete claim, close annotator
        // need to go to edit menu
        driver.findElement(By.id("annotator-delete")).click();
        Thread.sleep(1500);
        driver.findElement(By.id("claim-delete-confirm-btn")).click();
        Thread.sleep(5000);
    }

    public void createDrug(WebElement element, int x, int y) throws InterruptedException
    {
        Actions action = new Actions(driver);
        action.click();
        Thread.sleep(2000);
        action.moveToElement(element,x,y).doubleClick().build().perform();
        Thread.sleep(2000);
        driver.findElement(By.className("hl-adder-btn")).click();
        Thread.sleep(1000);
    }
}