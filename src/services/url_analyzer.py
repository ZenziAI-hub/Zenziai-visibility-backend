import requests
from bs4 import BeautifulSoup
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
from urllib.parse import urlparse
import datetime

# Download necessary NLTK data (only once)
try:
    nltk.data.find('tokenizers/punkt')
except (LookupError, Exception):
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except (LookupError, Exception):
    nltk.download('stopwords')

class URLAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def _get_readability_scores(self, text):
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        num_words = len(words)
        num_sentences = len(sentences)
        num_syllables = sum([self._count_syllables(word) for word in words])

        if num_sentences == 0 or num_words == 0:
            return {
                "word_count": num_words,
                "sentence_count": num_sentences,
                "avg_sentence_length": 0,
                "flesch_kincaid_grade": 12, # Default to high for unreadable
            }

        avg_sentence_length = num_words / num_sentences

        # Flesch-Kincaid Grade Level
        # FKRA = (0.39 * ASL) + (11.8 * ASW) - 15.59
        # ASL = average sentence length (number of words divided by number of sentences)
        # ASW = average syllables per word (number of syllables divided by number of words)
        if num_words > 0:
            avg_syllables_per_word = num_syllables / num_words
        else:
            avg_syllables_per_word = 0

        flesch_kincaid_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
        flesch_kincaid_grade = max(0, round(flesch_kincaid_grade))

        return {
            "word_count": num_words,
            "sentence_count": num_sentences,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "flesch_kincaid_grade": flesch_kincaid_grade,
        }

    def _count_syllables(self, word):
        # A simple syllable counter (can be improved with a proper library)
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"): # remove silent 'e'
            count -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels: # -le ending
            count += 1
        if count == 0:
            count += 1
        return count

    def _calculate_keyword_density(self, text, keywords):
        if not text or not keywords:
            return 0
        
        words = word_tokenize(text.lower())
        total_words = len(words)
        if total_words == 0:
            return 0

        keyword_counts = Counter(word for word in words if word in keywords)
        density = sum(keyword_counts.values()) / total_words * 100
        return round(density, 2)

    def _score_content_quality(self, soup, text_content):
        score = 0
        findings = []

        readability = self._get_readability_scores(text_content)
        word_count = readability["word_count"]
        flesch_kincaid = readability["flesch_kincaid_grade"]

        # Word count (penalize very short content, reward substantial content)
        if word_count < 200:
            score -= 20
            findings.append(f"Low word count ({word_count} words). Content may be too short.")
        elif word_count < 500:
            score += 10
            findings.append(f"Moderate word count ({word_count} words).")
        else:
            score += 20
            findings.append(f"Good word count ({word_count} words).")

        # Readability (Flesch-Kincaid)
        if flesch_kincaid <= 8:
            score += 15
            findings.append(f"Excellent readability (Flesch-Kincaid: {flesch_kincaid}).")
        elif flesch_kincaid <= 12:
            score += 10
            findings.append(f"Good readability (Flesch-Kincaid: {flesch_kincaid}).")
        else:
            score -= 10
            findings.append(f"Readability may be challenging (Flesch-Kincaid: {flesch_kincaid}).")

        # Use of multimedia
        images = soup.find_all('img')
        videos = soup.find_all('video') + soup.find_all('iframe', src=re.compile(r'(youtube.com|vimeo.com)'))
        if images or videos:
            score += 15
            findings.append(f"Multimedia detected (images: {len(images)}, videos: {len(videos)}).")
        else:
            score -= 5
            findings.append("No multimedia detected. Consider adding images/videos.")

        # Placeholder for keyword density and duplicate content (requires more context/external tools)
        findings.append("Keyword density and duplicate content detection not fully implemented.")

        final_score = max(0, min(100, score + 50)) # Normalize to 0-100, starting with a base of 50
        return {"score": final_score, "findings": findings}

    def _score_relevance_and_intent(self, soup, title, meta_description, text_content, keywords=None):
        score = 0
        findings = []
        
        if not keywords:
            # Simple keyword extraction from title and meta description
            all_words = word_tokenize((title + " " + meta_description).lower())
            keywords = [word for word in all_words if word.isalnum() and word not in self.stop_words]
            keywords = list(set(keywords)) # Unique keywords

        # Keyword prominence in title
        title_lower = title.lower()
        if any(kw in title_lower for kw in keywords):
            score += 20
            findings.append("Keywords found in page title.")
        else:
            findings.append("No prominent keywords found in page title.")

        # Keyword prominence in headings (H1, H2, H3)
        headings_text = " ".join([h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]).lower()
        if any(kw in headings_text for kw in keywords):
            score += 20
            findings.append("Keywords found in headings (H1-H3).")
        else:
            findings.append("No prominent keywords found in headings.")

        # Content alignment with meta description
        meta_desc_lower = meta_description.lower()
        if any(kw in meta_desc_lower for kw in keywords) and any(kw in text_content.lower() for kw in keywords):
            score += 15
            findings.append("Content aligns with meta description and keywords.")
        else:
            findings.append("Content may not fully align with meta description/keywords.")

        # Placeholder for Topic clustering and semantic relevance, Schema markup
        findings.append("Topic clustering, semantic relevance, and schema markup presence analysis pending.")

        final_score = max(0, min(100, score + 45)) # Normalize to 0-100, starting with a base of 45
        return {"score": final_score, "findings": findings}

    def _score_source_credibility(self, soup, url):
        score = 0
        findings = []

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # SSL/TLS certificate presence (basic check via URL scheme)
        if url.startswith("https://"):
            score += 20
            findings.append("SSL/TLS certificate detected (HTTPS).")
        else:
            score -= 10
            findings.append("No SSL/TLS certificate detected (HTTP). This negatively impacts credibility.")

        # Contact information availability (looking for common links)
        contact_links = soup.find_all('a', href=re.compile(r'(contact|about|team)', re.I))
        if contact_links:
            score += 15
            findings.append("Contact/About/Team links found.")
        else:
            score -= 5
            findings.append("No obvious Contact/About/Team links found.")

        # External link quality and quantity (simple count for now)
        external_links = [a['href'] for a in soup.find_all('a', href=True) if urlparse(a['href']).netloc != domain and a['href'].startswith(('http', 'https'))]
        if len(external_links) > 5:
            score += 10
            findings.append(f"Numerous external links ({len(external_links)}) detected. Quality check pending.")
        elif len(external_links) > 0:
            score += 5
            findings.append(f"Some external links ({len(external_links)}) detected. Quality check pending.")
        else:
            findings.append("Few or no external links detected.")

        # Placeholder for Domain authority, social proof, domain age (requires external APIs)
        findings.append("Domain authority, social proof, and domain age analysis pending (requires external APIs).")

        final_score = max(0, min(100, score + 55)) # Normalize to 0-100, starting with a base of 55
        return {"score": final_score, "findings": findings}

    def _score_content_structure(self, soup):
        score = 0
        findings = []

        # Proper heading hierarchy (H1 -> H2 -> H3)
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')

        if len(h1_tags) == 1:
            score += 20
            findings.append("Single H1 tag found (good practice).")
        elif len(h1_tags) > 1:
            score -= 10
            findings.append("Multiple H1 tags found. Consider using only one H1.")
        else:
            score -= 15
            findings.append("No H1 tag found. Essential for SEO and structure.")

        if h2_tags:
            score += 10
            findings.append(f"{len(h2_tags)} H2 tags found.")
        if h3_tags:
            score += 5
            findings.append(f"{len(h3_tags)} H3 tags found.")

        # Schema markup implementation (basic check for script tags with type application/ld+json)
        schema_scripts = soup.find_all('script', type='application/ld+json')
        if schema_scripts:
            score += 20
            findings.append(f"{len(schema_scripts)} JSON-LD schema script(s) detected.")
        else:
            findings.append("No JSON-LD schema markup detected.")

        # Mobile-friendly viewport meta tag
        viewport_meta = soup.find('meta', attrs={'name': 'viewport', 'content': re.compile(r'width=device-width', re.I)})
        if viewport_meta:
            score += 15
            findings.append("Mobile viewport meta tag detected.")
        else:
            score -= 10
            findings.append("Mobile viewport meta tag missing. Page may not be mobile-friendly.")

        # Placeholder for semantic HTML, internal linking, navigation clarity
        findings.append("Semantic HTML, internal linking, and navigation clarity analysis pending.")

        final_score = max(0, min(100, score + 30)) # Normalize to 0-100, starting with a base of 30
        return {"score": final_score, "findings": findings}

    def _score_freshness_and_timeliness(self, soup, response_headers):
        score = 0
        findings = []

        # Last-Modified HTTP header
        last_modified = response_headers.get('Last-Modified')
        if last_modified:
            try:
                # Parse date and compare with current date
                last_modified_date = datetime.datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
                age_days = (datetime.datetime.utcnow() - last_modified_date).days
                if age_days < 90:
                    score += 25
                    findings.append(f"Content recently modified ({age_days} days ago).")
                elif age_days < 365:
                    score += 15
                    findings.append(f"Content modified within the last year ({age_days} days ago).")
                else:
                    score -= 10
                    findings.append(f"Content last modified over a year ago ({age_days} days ago). May be outdated.")
            except ValueError:
                findings.append(f"Could not parse Last-Modified header: {last_modified}.")
        else:
            findings.append("No Last-Modified HTTP header found.")

        # Publication date metadata (looking for common meta tags or schema)
        pub_date_meta = soup.find('meta', property='article:published_time') or \
                        soup.find('meta', {'name': 'date'}) or \
                        soup.find('time')
        if pub_date_meta:
            score += 10
            findings.append("Publication date metadata detected.")
        else:
            findings.append("No explicit publication date metadata found.")

        # Placeholder for content update frequency signals, outdated content detection, news/blog recency
        findings.append("Content update frequency, outdated content detection, and news/blog recency analysis pending.")

        final_score = max(0, min(100, score + 40)) # Normalize to 0-100, starting with a base of 40
        return {"score": final_score, "findings": findings}

    def _score_user_engagement_potential(self, soup):
        score = 0
        findings = []

        # Call-to-action (CTA) presence (simple check for buttons/links with common CTA text)
        cta_elements = soup.find_all(lambda tag: tag.name in ['a', 'button'] and 
                                       any(keyword in tag.get_text().lower() for keyword in ['buy', 'shop', 'learn more', 'sign up', 'contact', 'get started']))
        if cta_elements:
            score += 20
            findings.append(f"Call-to-action elements detected ({len(cta_elements)}).")
        else:
            score -= 10
            findings.append("Few or no clear call-to-action elements found.")

        # Form availability (contact, newsletter, etc.)
        forms = soup.find_all('form')
        if forms:
            score += 15
            findings.append(f"{len(forms)} form(s) detected (e.g., contact, newsletter).")
        else:
            findings.append("No forms detected on the page.")

        # Social sharing buttons (common social media links)
        social_share_links = soup.find_all('a', href=re.compile(r'(facebook.com/sharer|twitter.com/share|linkedin.com/share)', re.I))
        if social_share_links:
            score += 10
            findings.append("Social sharing buttons detected.")
        else:
            findings.append("No obvious social sharing buttons found.")

        # Video/media embedded content (already checked in content quality, reuse if possible or re-check)
        videos = soup.find_all('video') + soup.find_all('iframe', src=re.compile(r'(youtube.com|vimeo.com)'))
        if videos:
            score += 10
            findings.append(f"Embedded video content detected ({len(videos)}).")
        else:
            findings.append("No embedded video content found.")

        # Placeholder for comments/discussion, internal link engagement, time-on-page estimation
        findings.append("Comments/discussion sections, internal link engagement, and time-on-page estimation analysis pending.")

        final_score = max(0, min(100, score + 45)) # Normalize to 0-100, starting with a base of 45
        return {"score": final_score, "findings": findings}

    def _score_technical_seo(self, soup, url, response_headers):
        score = 0
        findings = []

        # Mobile responsiveness (viewport meta tag already checked in content structure, re-check or assume)
        viewport_meta = soup.find('meta', attrs={'name': 'viewport', 'content': re.compile(r'width=device-width', re.I)})
        if viewport_meta:
            score += 15
            findings.append("Mobile viewport meta tag present (indicates mobile responsiveness).")
        else:
            score -= 10
            findings.append("Mobile viewport meta tag missing. Page may not be mobile-friendly.")

        # Canonical tag presence
        canonical_link = soup.find('link', rel='canonical')
        if canonical_link and canonical_link.get('href'):
            score += 15
            findings.append(f"Canonical tag found: {canonical_link['href']}.")
        else:
            findings.append("No canonical tag found. May lead to duplicate content issues.")

        # Image optimization (alt text, lazy loading - basic check)
        images_with_alt = [img for img in soup.find_all('img') if img.get('alt')]
        total_images = len(soup.find_all('img'))
        if total_images > 0:
            alt_text_ratio = len(images_with_alt) / total_images
            if alt_text_ratio > 0.75:
                score += 10
                findings.append(f"Most images have alt text ({len(images_with_alt)}/{total_images}).")
            elif alt_text_ratio > 0.25:
                score += 5
                findings.append(f"Some images have alt text ({len(images_with_alt)}/{total_images}).")
            else:
                findings.append(f"Few images have alt text ({len(images_with_alt)}/{total_images}). Consider adding alt text for accessibility and SEO.")
        else:
            findings.append("No images found on the page.")

        # Placeholder for Page load speed (Lighthouse), Core Web Vitals, XML sitemap, Robots.txt, 404 errors
        findings.append("Page load speed, Core Web Vitals, XML sitemap, Robots.txt, and 404 errors analysis pending (requires external tools/further crawling).")
        
        final_score = max(0, min(100, score + 40)) # Normalize to 0-100, starting with a base of 40
        return {"score": final_score, "findings": findings}

    def analyze_url(self, url):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title and meta description
            title = soup.title.string if soup.title else 'No title found'
            meta_description_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', property='og:description')
            meta_description = meta_description_tag['content'] if meta_description_tag else 'No meta description found'

            # Extract main text content (remove scripts, styles, and common navigation/footer elements)
            for script in soup(['script', 'style', 'header', 'footer', 'nav']):
                script.extract()
            text_content = soup.get_text(separator=' ', strip=True)

            # Perform analysis for each category
            content_quality_result = self._score_content_quality(soup, text_content)
            relevance_and_intent_result = self._score_relevance_and_intent(soup, title, meta_description, text_content)
            source_credibility_result = self._score_source_credibility(soup, url)
            content_structure_result = self._score_content_structure(soup)
            freshness_and_timeliness_result = self._score_freshness_and_timeliness(soup, response.headers)
            user_engagement_potential_result = self._score_user_engagement_potential(soup)
            technical_seo_result = self._score_technical_seo(soup, url, response.headers)

            # Calculate overall score (simple average for now)
            all_scores = [
                content_quality_result['score'],
                relevance_and_intent_result['score'],
                source_credibility_result['score'],
                content_structure_result['score'],
                freshness_and_timeliness_result['score'],
                user_engagement_potential_result['score'],
                technical_seo_result['score']
            ]
            overall_score_value = round(sum(all_scores) / len(all_scores)) if all_scores else 0

            return {
                "url": url,
                "overall_score": {
                    "value": overall_score_value,
                    "interpretation": "Aggregated score based on detailed analysis of 7 categories."
                },
                "content_quality": content_quality_result,
                "relevance_and_intent": relevance_and_intent_result,
                "source_credibility": source_credibility_result,
                "content_structure": content_structure_result,
                "freshness_and_timeliness": freshness_and_timeliness_result,
                "user_engagement_potential": user_engagement_potential_result,
                "technical_seo": technical_seo_result
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}
