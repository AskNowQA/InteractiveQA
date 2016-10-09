package tech.sda.iqa.sparql.jena;
import java.io.ByteArrayOutputStream;

import java.util.ArrayList;


import com.hp.hpl.jena.query.*;

public class OnehopRel {
	public static void main( String[] args ) {
		String sparql = "select distinct ?rel ?label where {"
				+ "<http://dbpedia.org/resource/Barack_Obama> ?rel ?x."
				+ "?rel <http://www.w3.org/2000/01/rdf-schema#label> ?label."
				+ "filter(langMatches(lang(?label),\"EN\")) }";

		Query query = QueryFactory.create(sparql); //s2 = the query above
		QueryExecution qExe = QueryExecutionFactory.sparqlService( "http://dbpedia.org/sparql", query );
		ResultSet results = qExe.execSelect();
		// ResultSetFormatter.out(System.out, results, query) ;

		//Represent in json
		ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
		ResultSetFormatter.outputAsJSON(outputStream, results);


		String json = new String(outputStream.toByteArray());
		// System.out.println(json);


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
		for (int i = 0; i < listOfPair.size(); i++){
			String p[] = listOfPair.get(i);
			System.out.println(p[0]+"::"+p[1]);
		}

	}
}