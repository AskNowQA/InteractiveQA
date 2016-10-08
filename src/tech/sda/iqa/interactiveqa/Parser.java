package tech.sda.iqa.interactiveqa;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;
import java.io.FileInputStream;
import java.io.InputStream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
//import org.aksw.asknow.util.XmlUtil;
import org.w3c.dom.*;
import org.xml.sax.InputSource;

import lombok.SneakyThrows;




/** Reads a NQS QALD benchmark template XML file and returns a set of QCT templates. */
public class Parser
{
	/**
	 * Parses the default benchmark (QALD-5 NQS)
	 * @return The list of NQS from QALD-5.*/
	public static List<Nqs> parse()
	{	
		return parse(()->Parser.class.getClassLoader().getResourceAsStream("resource/qald6test-nqs.xml"));
	}

	/** @param in supplies a NQS-modified QALD XML format benchmark. Needs to supply a fresh stream each time.
	 * @return a list of NQS as written in the benchmark in the same order. */
	@SneakyThrows
	// TODO: detailed exception handling later
	public static List<Nqs> parse(Supplier<InputStream> in)
	{
		List<Nqs> templates = new ArrayList<>();

		//Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(in.get());
		
		DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();

	     
	         // use the factory to create a documentbuilder
	         DocumentBuilder builder = factory.newDocumentBuilder();

	         // create a new document from input source
	         FileInputStream fis = new FileInputStream("resource/qald6test-nqs.xml");
	         InputSource is = new InputSource(fis);
	         Document doc = builder.parse(is);
		
		
		doc.getDocumentElement().normalize();
		//if(!XmlUtil.validateAgainstXSD(in.get(), Parser.class.getClassLoader().getResourceAsStream("nqs.xsd")))
		//{throw new IllegalArgumentException("QCT template file not valid against the XSD.");}
		
		NodeList nList = doc.getElementsByTagName("QALDquestions");
		//System.out.println(nList.getLength());
		for (int i = 0; i < nList.getLength(); i++)
		{
			Node nNode = nList.item(i);

			if (nNode.getNodeType() == Node.ELEMENT_NODE)
			{
				
				Element eElement = (Element) nNode;

				String queryId = eElement.getAttribute("QALDquestions id");
				String nlQuery = eElement.getElementsByTagName("Ques").item(0).getTextContent();
				String qct = eElement.getElementsByTagName("NQS").item(0).getTextContent();
				String givenSparql = "";
				templates.add(new Nqs(nlQuery,qct,queryId,givenSparql));
			}
		}
		return templates;
	}

}