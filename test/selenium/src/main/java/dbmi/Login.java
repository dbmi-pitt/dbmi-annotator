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
        System.out.println("TEST-user-login");        
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
        // driver.findElement(By.name("sourceURL")).sendKeys("http://localhost/PMC/PMC2686069.html");
        driver.findElement(By.name("sourceURL")).sendKeys("http://localhost/test/test.html");
        driver.findElement(By.xpath("//button[contains(.,'load')]")).click();
        Thread.sleep(1500);

        // import existing annotations
        driver.findElement(By.xpath("//button[contains(.,'Import')]")).click(); // import
        Thread.sleep(1500);

        WebElement firstP = driver.findElement(By.id("drug1"));

        // create drug mention 1
        Actions clickDrug1 = new Actions(driver);
        // action1.doubleClick(firstP).build().perform();
        System.out.println(firstP.getText());     
        System.out.println(firstP.getLocation()); 
        // int x = firstP.getLocation().getX();
        // int y = firstP.getLocation().getY();
        // System.out.println(x + " by " + y);
        // clickDrug1.moveByOffset(x, y).doubleClick().build().perform();
        clickDrug1.moveToElement(firstP,0,0).doubleClick().build().perform();
        // action1.moveByOffset(x,y).clickAndHold().moveByOffset(30,0).release().build().perform();
        Thread.sleep(2000);

        driver.findElement(By.className("hl-adder-btn")).click();
        Thread.sleep(1000);

        //move cursor to a new word, annotate drug 2
        Actions clickDrug2 = new Actions(driver);
        WebElement secondP = driver.findElement(By.id("drug2"));
        // x = secondP.getLocation().getX();
        // y = secondP.getLocation().getY();
        // System.out.println(x + " by " + y);
        // clickDrug2.moveByOffset(x, y).doubleClick().build().perform();
        clickDrug2.click();
        clickDrug2.moveToElement(secondP,0,0).doubleClick().build().perform();
        Thread.sleep(2000);

        driver.findElement(By.className("hl-adder-btn")).click();
        Thread.sleep(1000);

        //Highlight passage containing the 2 words

        // Actions move = new Actions(driver);
        // move.moveByOffset(-100,0).build().perform();

        //highlight until next element.
        WebElement next = driver.findElement(By.xpath("//h3[contains(text(), 'METHODS')]"));
        Actions highlight = new Actions(driver);
        // highlight.moveToElement(next,0,0).doubleClick().build().perform();
        System.out.println(firstP + "\n" + next);
        highlight.moveToElement(firstP,0,0).click();
        highlight.keyDown(Keys.SHIFT);
        highlight.moveToElement(next,0,0).click();
        highlight.keyUp(Keys.SHIFT);
        highlight.build().perform();
        // highlight.dragAndDrop(firstP, next).build().perform();
        // highlight.doubleClick().clickAndHold().moveByOffset(1,1).pause(1000).moveToElement(next,0,0).release().build().perform();
        Thread.sleep(2000);

        WebElement mp = driver.findElement(By.className("mp-menu-btn"));
        Actions claim = new Actions(driver);
        claim.moveToElement(mp).build().perform();
        driver.findElement(By.className("mp-main-menu-1")).click();
        Thread.sleep(2000);

        WebElement d1 =  driver.findElement(By.id("Drug1"));
        Select dropdown1 = new Select(d1);
        dropdown1.selectByVisibleText("warfarin");
        Thread.sleep(1000);

        WebElement d2 = driver.findElement(By.id("Drug2"));
        Select dropdown2 = new Select(d2);
        dropdown2.selectByVisibleText("ambrisentan");
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

    // @Test // TEST WITH NORMAL WEBPAGE (NOT IN ANNOTATIONPRESS)
    // public void test_user_login() throws InterruptedException {
    //     System.out.println("TEST-Highlight");
    //     //"http://localhost/test/test.html"
    //     driver.get("http://localhost/test.html");
    //     driver.manage().window().maximize();
    //     Thread.sleep(800);

    //     Actions clickDrug = new Actions(driver);
    //     WebElement firstP = driver.findElement(By.id("drug1"));
    //     WebElement secondP = driver.findElement(By.id("drug2"));
    //     // clickDrug.moveToElement(firstP,0,0).doubleClick().build().perform();
    //     // Thread.sleep(1000);
    //     // clickDrug.click().moveToElement(secondP,0,0).doubleClick().build().perform();
    //     // clickDrug.click().build().perform();
    //     // Thread.sleep(1000);

    //     WebElement aims = driver.findElement(By.xpath("//h3[contains(text(), 'AIMS')]"));
    //     WebElement methods = driver.findElement(By.xpath("//h3[contains(text(), 'METHODS')]"));
    //     Actions highlight = new Actions(driver);
    //     highlight.moveToElement(firstP,0,0).click();
    //     highlight.keyDown(Keys.SHIFT);
    //     highlight.moveToElement(methods,0,0).click();
    //     highlight.keyUp(Keys.SHIFT);
    //     highlight.build().perform();
    //     // highlight.dragAndDrop(firstP, next).build().perform();
    //     // highlight.moveToElement(firstP,0,0).clickAndHold().moveByOffset(0,200).release().perform();
    //     Thread.sleep(2000);
    // }

    @Test
    public void ClickHold(WebElement element) throws InterruptedException 
    {
        System.out.println("TEST-ClickHold");
        Actions action = new Actions(driver);
        action.doubleClick(element).build().perform();
        action.moveByOffset(255,368).doubleClick().build().perform();

        WebElement firstP = driver.findElement(By.xpath("/html/body/div[9]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/p[1]"));
        /*WebElement*/ firstP = driver.findElement(By.xpath("//p[text()='warfarin']"));

        

        System.out.println(firstP.getText());     
        System.out.println(firstP.getLocation());      

        int x = firstP.getLocation().getX();
        int y = firstP.getLocation().getY();

        Actions action1 = new Actions(driver);
        action1.moveByOffset(x, y).doubleClick().build().perform();

        action1.moveByOffset(68,568).clickAndHold().moveByOffset(168,568).perform();
        // Thread.sleep(2000);
        // action1.MoveToElement(element).Release();
    }

    // @Test
    // public void test_user_register() throws InterruptedException {

    //     driver.get(appUrl);        
    //     Thread.sleep(2000);
    //     driver.findElement(By.linkText("Register")).click();        
    //     Thread.sleep(2000);
    //     driver.findElement(By.name("email")).sendKeys("test@gmail.com");
    //     driver.findElement(By.name("username")).sendKeys("tester");
    //     driver.findElement(By.name("password")).sendKeys("testtest");
    //     driver.findElement(By.name("repassword")).sendKeys("testtest");
        
    //     Thread.sleep(2000);
    //     driver.findElement(By.xpath("//button[contains(.,'Register')]")).click();
    //     Thread.sleep(2000);
    // }


}
