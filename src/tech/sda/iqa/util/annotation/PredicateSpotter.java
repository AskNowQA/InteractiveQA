package tech.sda.iqa.util.annotation;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;

import tech.sda.iqa.interactiveqa.Nqs;

public class PredicateSpotter {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

	}

	public static ArrayList<String> getRelation(Nqs n) {
		// TODO Auto-generated method stub
		ArrayList<String> Predicate = new ArrayList<String>();
		//Set<String> Predicate = new HashSet<String>();
		//extract predicate candidate from NQS
		//String sc;
		String temp = n.nlQuery;
		//		try{
		//			temp =n.getDesire();
		//				//count(xyz) --> xyz
		//			if(temp.contains("(")&&temp.contains(")"))
		//				temp = temp.substring(temp.indexOf("(")+1, temp.indexOf(")"));
		//			
		//			Predicate.add(temp);
		//			Predicate.add(n.getRelation2());
		//			Predicate=clearNoise (Predicate);
		//
		//		}
		//		catch(Exception e){
		//			//Predicate = null;
		//			
		//		}
		//temp = cleanNQS(n.nlQuery,n.nqs);
		if (temp.contains( n.getWh() ) ){ 			//remove WH
			temp= temp.replace(n.getWh(), "");
			temp=temp.replace("?", "");
		}
		
		//temp= temp.replace(n.getRelation1(), "");   //remove R1
	
		temp= removeStopWord(temp);					//remove stopwords
		
		//System.out.println(temp);
		temp = removeEntity(temp,n.resDBSpotted); //
		//System.out.println(temp);
		
		//String to Set
		String[] words = temp.split("#");
		for(int i=0;i<words.length;i++){
			if(!words[i].equalsIgnoreCase("?"))
			Predicate.add(words[i]);
		}
		return  Predicate;
	}
	private static String removeEntity(String temp, Set<String> resDBSpotted) {
		for(String res : resDBSpotted){
			//System.out.println(temp);
			 //spliting spotted word and its uri
					
			temp = temp.replace(res,"");
			//System.out.println(temp);
		}
		
		return temp.trim();
	}

	private static String removeStopWord(String temp) {
		String[] stopwords = { "of","list","Give", "me", "all","and","or",
				"have","had","has","more","through","than","the",
				"often","seldom","with","that","main",
				"does","did","do","as","is","are","was","were","a","an",
				"by","from","to","for","need","I","you","in","on"};
		//"a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always",
		//"am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at",
		//"back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", 
		//"beyond", "bill", "both", "bottom","but", "by", "call", "can", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do",
		//"done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", 
		//"everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four",
		//"from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", 
		//"hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", 
		//"keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", 
		//"mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor",
		//"not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", 
		//"out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", 
		//"she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", 
		//"still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", 
		//"therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", 
		//"too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", 
		//"whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
		//"who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the");
		try{
			String[] words = temp.split("\\s+");
			
			for(String sw: stopwords){
				for(int i=0;i<words.length;i++){
					
						if(sw.equalsIgnoreCase(words[i])){
							words[i]="";
						}
				}
			}
			temp="";//clear
			for(int i=0;i<words.length;i++){
				temp=temp+" "+words[i];
			}
			
		}
		catch(Exception e){

		}


		return temp.trim();
	}

	private static String cleanNQS(String nlQuery, String nqs) {

		return null;
	}

	private static Set<String> clearNoise(Set<String> predicate) {
		// TODO Auto-generated method stub
		String[] stopwords = { "of","list","Give me all",
				"have","had","has","more","through","than","the","and","or","both",
				"does","did","do","as","is","are","was","were","a","an",
				"by","from","to","for","need","I","you","in","on"};
		Set<String> temp = new HashSet<String>();
		for(String p : predicate){
			String[] words = p.split("\\s+");
			//System.out.print(p+"-");
			for(int i=0;i<words.length;i++){

				for(String s: stopwords){
					//System.out.print(s + "="+words[i]+";");
					if(s.equalsIgnoreCase(words[i])){
						words[i]="";
						//System.out.println("HIT");break;
					}
				}
				if(!words[i].equalsIgnoreCase(""))
					temp.add(words[i]);
			}
			//String word = words.toString();
			//System.out.print("777"+words.toString());//cleaning
			//temp.add(word);
			//correct word
			//if not null: add to candidate list

		}
		//System.out.println(temp);
		return temp;
	}


}
