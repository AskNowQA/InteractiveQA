package tech.sda.iqa.sparql;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;

import com.hp.hpl.jena.query.ResultSetFormatter;

import tech.sda.iqa.sparql.jena.QueryExecutor;

public class OneHopRelationQuery {
	
//	select distinct ?rel ?label where {
//		{<http://dbpedia.org/resource/Germany> ?rel ?x.}
//		UNION
//		{?x ?rel <http://dbpedia.org/resource/Germany>.}
//		?rel <http://www.w3.org/2000/01/rdf-schema#label> 
//		?label.filter(langMatches(lang(?label),"EN")) }

	public static ArrayList<String[]> getPredicateList(String dbr){
		String sparql = "select distinct ?rel ?label where {"
				+ "{"+dbr+" ?rel ?x.}"
				+ "UNION"
				+ "{ ?x ?rel" +dbr+" .}"
				+ "?rel <http://www.w3.org/2000/01/rdf-schema#label> ?label."
				+ "filter(langMatches(lang(?label),\"EN\")) }";
		System.out.println(sparql);
		ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
		ResultSetFormatter.outputAsJSON(outputStream, QueryExecutor.query(sparql));
		
		String json = new String(outputStream.toByteArray());
		//System.out.println(json);
		String[] temp = new String[2]; 
		ArrayList<String[]> listOfPair = new ArrayList<String[]>();
		String t=json;
		for(int i=0;i<=json.length();i++){

			try{
				t=t.substring(t.indexOf("\"rel\":"));
				temp[0]=t.substring(t.indexOf("\"value\"")+10,t.indexOf("}")-2 );  
				t=t.substring(t.indexOf("\"label\":"));
				temp[1]=t.substring(t.indexOf("\"value\"")+10,t.indexOf("}")-2 );
				listOfPair.add(new String[] {temp[0], temp[1]}); 
			}
			catch (Exception e){
				break;
			}
		}
//		for (int i = 0; i < listOfPair.size(); i++){
//			String p[] = listOfPair.get(i);
//			//System.out.println(p[0]+"::"+p[1]);
//		}
		
		return listOfPair;
	}
}
