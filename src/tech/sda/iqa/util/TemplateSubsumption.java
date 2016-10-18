package tech.sda.iqa.util;
/*
 * SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Turkmenistan> <http://dbpedia.org/ontology/language> ?uri }
 * --> SELECT (COUNT(DISTINCT ?uri) as ?c) WHERE {  <http://dbpedia.org/resource/Turkmenistan> <http://dbpedia.org/ontology/language> ?uri . }
 * 
 */
public class TemplateSubsumption {
	public static void main(String[] args){ 
		//testQALD();
		System.out.println(countTemplate("SELECT DISTINCT ?uri WHERE { <http://dbpedia.org/resource/Turkmenistan> <http://dbpedia.org/ontology/language> ?uri }"));
	
	}
 static String countTemplate(String q){
	 q = q.replace("DISTINCT ?uri", "( COUNT ( DISTINCT ?uri ) as ?c )");
	return q;
	 }
 
}
