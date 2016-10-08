package tech.sda.iqa.benchmark;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.regex.Pattern;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.TransformerFactoryConfigurationError;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

import tech.sda.iqa.interactiveqa.Nqs;
import tech.sda.iqa.nqs.QueryBuilder;
import tech.sda.iqa.nqs.ner_resolver;

/*
 * 1. Read QALD training Set [id, question, SPARQL]
 * 2. Get NQS
 * 3. Parse NQS to Asknow's QueryTypeSelection Decision Tree
 * 4. Efficiency Score : TODO probability measure  
 */
public class SPARQLtypeSelction {
	private static QueryBuilder qb;
	static ArrayList<String> nertags = new ArrayList<String>();


	public static void main(String[] args) {
		// TODO Auto-generated method stub
		qb = new QueryBuilder();
		readQALDfile();
		//System.out.println(getNQS("Who was the first president of independent India?"));
	}

	static String getNQS(String ques){
		//qb = new QueryBuilder();
		qb.setQuery(ques);
		qb.buildQuery();
		String nqs = qb.getCharacterizedString();
		//nertags = ner_resolver.nertag;
		return nqs;
	}

	static void readQALDfile() {

		//Variable for statistics
		int counter_LIST=0, hit_LIST =0;
		int counter_BOOLEAN=0, hit_BOOLEAN =0;
		int counter_COUNT=0, hit_COUNT =0;
		int counter_RANK=0, hit_RANK =0;
		int counter_DATA=0, hit_DATA =0;
		//--------//
		DocumentBuilderFactory qaldFactory = DocumentBuilderFactory.newInstance();
		DocumentBuilder qaldBuilder;

		JSONParser parser = new JSONParser();

		try {
			qaldBuilder = qaldFactory.newDocumentBuilder();
			Document doc = qaldBuilder.newDocument();
			Element mainRootElement = doc.createElementNS("http://github.com/SmartDataAnalytics/InteractiveQA", "NQSforQALD");
			doc.appendChild(mainRootElement);

			Object obj = parser.parse(new FileReader("resource/qald6training.json"));

			JSONObject jsonObject = (JSONObject) obj;
			JSONArray quald = (JSONArray) jsonObject.get("questions");
			Iterator<JSONObject> questions = quald.iterator();
			while (questions.hasNext()) {
				JSONObject quesObj = questions.next();
				Object ids = quesObj.get("id");

				String ques = null;
				String sparql = null;
				String type=null;//TODO:boolean
				//ystem.out.println(id );
				JSONArray alllang = (JSONArray) quesObj.get("question");
				Iterator<JSONObject> onelang = alllang.iterator();
				while (onelang.hasNext()) {
					JSONObject engques = onelang.next();
					ques = (String) engques.get("string");
					JSONObject sparqls = (JSONObject) quesObj.get("query");
					sparql = (String) sparqls.get("sparql");
					System.out.println(sparql);
					break;
				}
				String nqs = getNQS(ques);
				if(sparql==null){
					mainRootElement.appendChild(getNQSxml(doc, ids.toString() , ques, "empty",nqs,""));
				}
				else
				{
					String nqs_stype =parseNQS(ques,nqs);
					String sparql_stype=parseSparql(sparql);

					if(sparql_stype.contains("LIST"))
						{ counter_LIST++; 
							if(nqs_stype.contains("LIST"))
								hit_LIST ++;
						}
					else if(sparql_stype.contains("BOOLEAN"))
						{ counter_BOOLEAN++; 
							if(nqs_stype.contains("BOOLEAN"))
								hit_BOOLEAN ++;
					}
					else if(sparql_stype.contains("COUNT"))
						{ counter_COUNT++; 
							if(nqs_stype.contains("COUNT"))
								hit_COUNT++;
					}
					else if(sparql_stype.contains("RANK"))
						{ counter_RANK++; 
							if(nqs_stype.contains("RANK"))
								hit_RANK++;
						}
					else if(sparql_stype.contains("DATA"))
					{ counter_DATA++; 
					if(nqs_stype.contains("DATA"))
						hit_DATA++;
					}

					type= nqs_stype+ ":" + sparql_stype;

					mainRootElement.appendChild(getNQSxml(doc, ids.toString() , ques, sparql,nqs,type));

				}

			}
			System.out.println("output");
			System.out.println("total LIST query = "+ counter_LIST +"  efficency = "+ (float)hit_LIST/counter_LIST);
			System.out.println("total BOOLEAN query = "+ counter_BOOLEAN +"  efficency = "+ (float)hit_BOOLEAN/counter_BOOLEAN);
			System.out.println("total COUNT query = "+ counter_COUNT +"  efficency = "+ (float)hit_COUNT/counter_COUNT);
			System.out.println("total RANK query = "+ counter_RANK +"  efficency = "+ (float)hit_RANK/counter_RANK);
			System.out.println("total DATA query = "+ counter_DATA +"  efficency = "+ (float)hit_DATA/counter_DATA);
			try{
				//out.println( output);
				Transformer transformer = TransformerFactory.newInstance().newTransformer();
				transformer.setOutputProperty(OutputKeys.INDENT, "yes"); 
				DOMSource source = new DOMSource(doc);
				StreamResult result = new StreamResult(new File("resource/zqald6test-nqs.xml"));
				//StreamResult console = new StreamResult(System.out);
				transformer.transform(source, result);
				//out.println( console);

				System.out.println("\nXML DOM Created Successfully..");


			} catch (TransformerConfigurationException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (TransformerFactoryConfigurationError e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (TransformerException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ParseException e) {
			e.printStackTrace();
		} catch (ParserConfigurationException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}




	}


	private static String parseSparql(String sparql) {
		sparql=sparql.toLowerCase();

		if (sparql.contains("ask")){
			return "BOOLEAN";
		}

		else if (sparql.contains("count ")||sparql.contains("count(")){
			return "COUNT" ;
		}
		else if (sparql.contains("order by")){
			return "RANK";
		}
		return "LIST";
	}

	private static String parseNQS(String ques,String nqs) {
		Nqs q1 = new Nqs(ques,nqs,"","");
		Pattern superlativeWordList = Pattern.compile("highest|lowest|deepest|fastest|longest|largest|youngest|oldest|heaviest|lightest|tallest|shortest");

		if (q1.nqs.contains("] =  list")){
			return "LIST";
		}
		else if (q1.nqs.contains("[Concepts] = [")){
			return "BOOLEAN" ;
		}
		else if (q1.nlQuery.toLowerCase().contains("how many")){
			return "COUNT";
		}
		else if (superlativeWordList.matcher(q1.nlQuery).find()){
			return "RANK";
		}
		else 
		{
			return "LIST";
		}
	}

	private static Node getNQSxml(Document doc, String id, String ques, String sparql,String nqs,String type) {
		Element nqsxml = doc.createElement("QALDquestions");
		nqsxml.setAttribute("id", id);
		nqsxml.appendChild(getNQSxmlElements(doc, nqsxml, "Ques", ques));
		nqsxml.appendChild(getNQSxmlElements(doc, nqsxml, "SPARQL", sparql));
		nqsxml.appendChild(getNQSxmlElements(doc, nqsxml, "NQS", nqs));
		nqsxml.appendChild(getNQSxmlElements(doc, nqsxml, "TYPE", type));
		return nqsxml;
	}

	// utility method to create text node
	private static Node getNQSxmlElements(Document doc, Element element, String name, String value) {
		Element node = doc.createElement(name);
		node.appendChild(doc.createTextNode(value));
		return node;
	}


}
