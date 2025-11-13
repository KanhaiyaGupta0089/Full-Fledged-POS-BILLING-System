import { useState, useEffect } from 'react';
import { Plus, Search, Eye, Sparkles, Image as ImageIcon, Video, FileText, Share2, Settings, Calendar, TrendingUp, BarChart3, X, Save, Download, Wand2, Hash, MessageSquare, CheckCircle, Clock, AlertCircle, Maximize2, ExternalLink } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import api from '../services/api';
import toast from 'react-hot-toast';
import useAuthStore from '../store/authStore';

export default function Marketing() {
  const { isAuthenticated, token } = useAuthStore();
  const [campaigns, setCampaigns] = useState([]);
  const [contents, setContents] = useState([]);
  const [socialAccounts, setSocialAccounts] = useState([]);
  const [posts, setPosts] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTab, setSelectedTab] = useState('campaigns'); // 'campaigns', 'contents', 'social', 'posts'
  
  // Modals
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [showContentModal, setShowContentModal] = useState(false);
  const [showSocialModal, setShowSocialModal] = useState(false);
  const [showPostModal, setShowPostModal] = useState(false);
  const [showAIGenerateModal, setShowAIGenerateModal] = useState(false);
  const [viewingPoster, setViewingPoster] = useState(null);
  
  // Form Data
  const [campaignFormData, setCampaignFormData] = useState({
    name: '',
    description: '',
    campaign_type: 'product_promotion',
    status: 'draft',
    budget: '',
    start_date: '',
    end_date: '',
    target_audience: '',
    use_ai_content: true,
    ai_style: 'professional',
    ai_tone: 'friendly',
  });
  
  const [contentFormData, setContentFormData] = useState({
    campaign_id: '',
    content_type: 'poster',
    title: '',
    description: '',
    headline: '',
    call_to_action: '',
    hashtags: '',
    product_id: '',
    custom_text: '',
    text_color: '#000000',
    background_color: '#FFFFFF',
    font_style: 'Arial',
    font_size: 24,
    image: null,
  });
  const [imagePreview, setImagePreview] = useState(null);
  
  const [aiGenerateData, setAIGenerateData] = useState({
    campaign_id: '',
    product_id: '',
    content_type: 'poster',
    prompt: '',
    style: 'professional',
    tone: 'friendly',
    generate_image: false,
    generate_video: false,
    generate_multiple_posters: false,
    poster_count: 3,
    image_width: 1024,
    image_height: 1024,
    video_duration: 15,
  });
  
  const [socialFormData, setSocialFormData] = useState({
    platform: 'facebook',
    account_name: '',
    account_id: '',
    access_token: '',
  });
  
  const [postFormData, setPostFormData] = useState({
    content_id: '',
    social_account_id: '',
    caption: '',
    scheduled_time: '',
  });
  
  const [editingCampaign, setEditingCampaign] = useState(null);
  const [editingContent, setEditingContent] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    // Check if user is authenticated before fetching
    if (!isAuthenticated || !token) {
      toast.error('Please log in to access marketing features');
      return;
    }
    fetchData();
  }, [selectedTab, isAuthenticated, token]);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchCampaigns(),
        fetchContents(),
        fetchSocialAccounts(),
        fetchPosts(),
        fetchProducts(),
      ]);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/marketing/campaigns/');
      setCampaigns(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch campaigns:', error);
    }
  };

  const fetchContents = async () => {
    try {
      const response = await api.get('/marketing/contents/');
      setContents(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch contents:', error);
    }
  };

  const fetchSocialAccounts = async () => {
    try {
      const response = await api.get('/marketing/social-accounts/');
      setSocialAccounts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch social accounts:', error);
    }
  };

  const fetchPosts = async () => {
    try {
      const response = await api.get('/marketing/posts/');
      setPosts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/products/');
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };

  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    try {
      if (editingCampaign) {
        await api.patch(`/marketing/campaigns/${editingCampaign.id}/`, campaignFormData);
        toast.success('Campaign updated');
      } else {
        await api.post('/marketing/campaigns/', campaignFormData);
        toast.success('Campaign created');
      }
      setShowCampaignModal(false);
      setEditingCampaign(null);
      resetCampaignForm();
      fetchCampaigns();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save campaign');
    }
  };

  const handleGenerateAIContent = async (e) => {
    e.preventDefault();
    try {
      if (!aiGenerateData.campaign_id) {
        toast.error('Please select a campaign');
        return;
      }
      
      setGenerating(true);
      // Prepare data - convert strings to integers and handle empty values
      const requestData = {
        content_type: aiGenerateData.content_type,
        prompt: aiGenerateData.prompt || '',
        style: aiGenerateData.style,
        tone: aiGenerateData.tone,
        campaign_type: aiGenerateData.campaign_type || 'product_promotion',
        generate_image: aiGenerateData.generate_image || false,
        generate_video: aiGenerateData.generate_video || false,
        generate_multiple_posters: aiGenerateData.generate_multiple_posters || false,
        poster_count: parseInt(aiGenerateData.poster_count) || 3,
        image_width: parseInt(aiGenerateData.image_width) || 1024,
        image_height: parseInt(aiGenerateData.image_height) || 1024,
        video_duration: parseInt(aiGenerateData.video_duration) || 15,
      };
      
      // Only include product_id if it's a valid number
      if (aiGenerateData.product_id && aiGenerateData.product_id !== '') {
        const productId = parseInt(aiGenerateData.product_id);
        if (!isNaN(productId)) {
          requestData.product_id = productId;
        }
      }
      
      const response = await api.post(`/marketing/campaigns/${aiGenerateData.campaign_id}/generate_content/`, requestData);
      
      // Handle multiple posters response (array) or single content (object)
      if (Array.isArray(response.data)) {
        toast.success(`Successfully generated ${response.data.length} poster variations!`);
      } else {
        toast.success('AI content generated successfully!');
      }
      
      setShowAIGenerateModal(false);
      setAIGenerateData({
        campaign_id: '',
        product_id: '',
        content_type: 'poster',
        prompt: '',
        style: 'professional',
        tone: 'friendly',
        generate_image: false,
        generate_video: false,
        generate_multiple_posters: false,
        poster_count: 3,
        image_width: 1024,
        image_height: 1024,
        video_duration: 15,
      });
      fetchContents();
      fetchCampaigns();
    } catch (error) {
      console.error('Generate content error:', error.response?.data);
      const errorMsg = error.response?.data?.detail || 
                      error.response?.data?.error || 
                      (error.response?.data?.product_id ? error.response.data.product_id[0] : null) ||
                      'Failed to generate content';
      toast.error(errorMsg);
    } finally {
      setGenerating(false);
    }
  };

  const handleCreateContent = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      Object.keys(contentFormData).forEach(key => {
        if (contentFormData[key] !== null && contentFormData[key] !== undefined && contentFormData[key] !== '') {
          formData.append(key, contentFormData[key]);
        }
      });
      
      if (editingContent) {
        await api.patch(`/marketing/contents/${editingContent.id}/`, formData);
        toast.success('Content updated');
      } else {
        await api.post('/marketing/contents/', formData);
        toast.success('Content created');
      }
      setShowContentModal(false);
      setEditingContent(null);
      resetContentForm();
      fetchContents();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save content');
    }
  };

  const handleConnectSocial = async (platform) => {
    try {
      const redirectUri = `${window.location.origin}/auth/callback`;
      const response = await api.get(`/marketing/social-accounts/auth_url/?platform=${platform}&redirect_uri=${encodeURIComponent(redirectUri)}`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Failed to get auth URL');
    }
  };

  const handlePublishPost = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/marketing/posts/publish/', postFormData);
      toast.success('Post published successfully!');
      setShowPostModal(false);
      resetPostForm();
      fetchPosts();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to publish post');
    }
  };

  const resetCampaignForm = () => {
    setCampaignFormData({
      name: '',
      description: '',
      campaign_type: 'product_promotion',
      status: 'draft',
      budget: '',
      start_date: '',
      end_date: '',
      target_audience: '',
      use_ai_content: true,
      ai_style: 'professional',
      ai_tone: 'friendly',
    });
  };

  const resetContentForm = () => {
    setContentFormData({
      campaign_id: '',
      content_type: 'poster',
      title: '',
      description: '',
      headline: '',
      call_to_action: '',
      hashtags: '',
      product_id: '',
      custom_text: '',
      text_color: '#000000',
      background_color: '#FFFFFF',
      font_style: 'Arial',
      font_size: 24,
      image: null,
    });
    setImagePreview(null);
  };

  const resetPostForm = () => {
    setPostFormData({
      content_id: '',
      social_account_id: '',
      caption: '',
      scheduled_time: '',
    });
  };

  if (loading) {
    return (
      <DashboardLayout title="Marketing & AI Ads">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Marketing & AI-Powered Ads">
      <div className="p-6 space-y-6">
        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setSelectedTab('campaigns')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'campaigns'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Campaigns
          </button>
          <button
            onClick={() => setSelectedTab('contents')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'contents'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <ImageIcon className="w-4 h-4 inline mr-2" />
            Ad Contents
          </button>
          <button
            onClick={() => setSelectedTab('social')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'social'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <Share2 className="w-4 h-4 inline mr-2" />
            Social Media
          </button>
          <button
            onClick={() => setSelectedTab('posts')}
            className={`px-4 py-2 font-medium ${
              selectedTab === 'posts'
                ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400'
                : 'text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Posts
          </button>
        </div>

        {/* Campaigns Tab */}
        {selectedTab === 'campaigns' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search campaigns..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setSelectedCampaign(null);
                    setShowAIGenerateModal(true);
                  }}
                  className="btn-primary"
                >
                  <Wand2 className="w-4 h-4 mr-2" />
                  AI Generate
                </button>
                <button
                  onClick={() => {
                    setEditingCampaign(null);
                    resetCampaignForm();
                    setShowCampaignModal(true);
                  }}
                  className="btn-primary"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Campaign
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaigns.filter(c => 
                c.name?.toLowerCase().includes(searchQuery.toLowerCase())
              ).map((campaign) => (
                <div key={campaign.id} className="card p-6 hover:shadow-lg transition-shadow">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{campaign.name}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{campaign.campaign_type.replace('_', ' ')}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      campaign.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                      campaign.status === 'paused' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                      campaign.status === 'completed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                      'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                    }`}>
                      {campaign.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2">{campaign.description || 'No description'}</p>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      Budget: ₹{parseFloat(campaign.budget || 0).toLocaleString('en-IN')}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedCampaign(campaign);
                        setAIGenerateData({ ...aiGenerateData, campaign_id: campaign.id });
                        setShowAIGenerateModal(true);
                      }}
                      className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    >
                      <Sparkles className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contents Tab */}
        {selectedTab === 'contents' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search contents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>
              <button
                onClick={() => {
                  setEditingContent(null);
                  resetContentForm();
                  setShowContentModal(true);
                }}
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Content
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {contents.filter(c => 
                c.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                c.description?.toLowerCase().includes(searchQuery.toLowerCase())
              ).map((content) => (
                <div key={content.id} className="card p-6 hover:shadow-lg transition-shadow">
                  {content.image && (
                    <div className="relative group mb-4">
                      <img
                        src={content.image}
                        alt={content.title}
                        className="w-full h-48 object-cover rounded-lg"
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 rounded-lg flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                        <button
                          onClick={() => {
                            setViewingPoster(content);
                          }}
                          className="bg-white text-gray-900 px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-gray-100 transition-colors"
                          title="View Full Size"
                        >
                          <Maximize2 className="w-4 h-4" />
                          View
                        </button>
                        <a
                          href={content.image}
                          download={`${content.title || 'poster'}_${content.id}.png`}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors"
                          title="Download Poster"
                        >
                          <Download className="w-4 h-4" />
                          Download
                        </a>
                      </div>
                    </div>
                  )}
                  {content.video && (
                    <div className="relative mb-4">
                      <video
                        src={content.video}
                        className="w-full h-48 object-cover rounded-lg"
                        controls
                        poster={content.thumbnail}
                      />
                    </div>
                  )}
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{content.title || 'Untitled'}</h3>
                    {content.ai_generated && (
                      <Sparkles className="w-5 h-5 text-purple-500" title="AI Generated" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-4 line-clamp-2">{content.description || 'No description'}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500 dark:text-gray-400">{content.content_type}</span>
                    <div className="flex gap-2">
                      {content.is_approved ? (
                        <CheckCircle className="w-5 h-5 text-green-500" title="Approved" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-yellow-500" title="Pending Approval" />
                      )}
                      {content.image && (
                        <>
                          <button
                            onClick={() => {
                              setViewingPoster(content);
                            }}
                            className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                            title="View Full Size"
                          >
                            <Maximize2 className="w-4 h-4" />
                          </button>
                          <a
                            href={content.image}
                            download={`${content.title || 'poster'}_${content.id}.png`}
                            className="text-green-600 hover:text-green-900 dark:text-green-400"
                            title="Download Poster"
                            onClick={(e) => {
                              e.stopPropagation();
                            }}
                          >
                            <Download className="w-4 h-4" />
                          </a>
                        </>
                      )}
                      <button
                        onClick={() => {
                          setEditingContent(content);
                          setContentFormData({
                            campaign_id: content.campaign,
                            content_type: content.content_type,
                            title: content.title || '',
                            description: content.description || '',
                            headline: content.headline || '',
                            call_to_action: content.call_to_action || '',
                            hashtags: content.hashtags || '',
                            product_id: content.product || '',
                            custom_text: content.custom_text || '',
                            text_color: content.text_color || '#000000',
                            background_color: content.background_color || '#FFFFFF',
                            font_style: content.font_style || 'Arial',
                            font_size: content.font_size || 24,
                          });
                          setImagePreview(null);
                          setShowContentModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                        title="Edit Content"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Social Media Tab */}
        {selectedTab === 'social' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Connected Accounts</h2>
              <button
                onClick={() => {
                  setSocialFormData({
                    platform: 'facebook',
                    account_name: '',
                    account_id: '',
                    access_token: '',
                  });
                  setShowSocialModal(true);
                }}
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                Connect Account
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {socialAccounts.map((account) => (
                <div key={account.id} className="card p-6">
                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      account.platform === 'facebook' ? 'bg-blue-500' :
                      account.platform === 'instagram' ? 'bg-pink-500' :
                      account.platform === 'twitter' ? 'bg-sky-500' :
                      'bg-gray-500'
                    }`}>
                      <Share2 className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white capitalize">{account.platform}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{account.account_name}</p>
                    </div>
                    {account.is_connected ? (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    ) : (
                      <AlertCircle className="w-5 h-5 text-yellow-500" />
                    )}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                    <p>Followers: {account.follower_count.toLocaleString()}</p>
                    <p>Posts: {account.posts_count || 0}</p>
                  </div>
                  <button
                    onClick={() => handleConnectSocial(account.platform)}
                    className="btn-secondary w-full"
                  >
                    {account.is_connected ? 'Reconnect' : 'Connect'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Posts Tab */}
        {selectedTab === 'posts' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="text"
                    placeholder="Search posts..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="input-field pl-10 w-full"
                  />
                </div>
              </div>
              <button
                onClick={() => {
                  resetPostForm();
                  setShowPostModal(true);
                }}
                className="btn-primary"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create Post
              </button>
            </div>

            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-800">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Platform</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Content</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Scheduled</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Engagement</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                    {posts.filter(p => 
                      p.caption?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                      p.content_title?.toLowerCase().includes(searchQuery.toLowerCase())
                    ).map((post) => (
                      <tr key={post.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="capitalize text-sm font-medium text-gray-900 dark:text-white">{post.platform_name}</span>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-sm text-gray-900 dark:text-white line-clamp-2">{post.content_title || 'Untitled'}</p>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            post.status === 'published' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                            post.status === 'scheduled' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                            post.status === 'failed' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                            'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                          }`}>
                            {post.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {post.scheduled_time ? new Date(post.scheduled_time).toLocaleString() : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          <div className="flex gap-4">
                            <span>❤️ {post.likes || 0}</span>
                            <span>💬 {post.comments || 0}</span>
                            <span>👁️ {post.views || 0}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400">
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Campaign Modal */}
        {showCampaignModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                  {editingCampaign ? 'Edit Campaign' : 'Create Campaign'}
                </h2>
                <form onSubmit={handleCreateCampaign} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Campaign Name *</label>
                      <input
                        type="text"
                        required
                        value={campaignFormData.name}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, name: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Campaign Type</label>
                      <select
                        value={campaignFormData.campaign_type}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, campaign_type: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="product_promotion">Product Promotion</option>
                        <option value="brand_awareness">Brand Awareness</option>
                        <option value="seasonal_sale">Seasonal Sale</option>
                        <option value="new_product">New Product Launch</option>
                        <option value="event">Event Promotion</option>
                        <option value="custom">Custom Campaign</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
                      <select
                        value={campaignFormData.status}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, status: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="draft">Draft</option>
                        <option value="active">Active</option>
                        <option value="paused">Paused</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Budget</label>
                      <input
                        type="number"
                        step="0.01"
                        value={campaignFormData.budget}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, budget: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Start Date</label>
                      <input
                        type="date"
                        value={campaignFormData.start_date}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, start_date: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">End Date</label>
                      <input
                        type="date"
                        value={campaignFormData.end_date}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, end_date: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                      <textarea
                        value={campaignFormData.description}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, description: e.target.value })}
                        className="input-field w-full"
                        rows="3"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">AI Style</label>
                      <select
                        value={campaignFormData.ai_style}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, ai_style: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="creative">Creative</option>
                        <option value="modern">Modern</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">AI Tone</label>
                      <select
                        value={campaignFormData.ai_tone}
                        onChange={(e) => setCampaignFormData({ ...campaignFormData, ai_tone: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="friendly">Friendly</option>
                        <option value="formal">Formal</option>
                        <option value="humorous">Humorous</option>
                        <option value="persuasive">Persuasive</option>
                      </select>
                    </div>
                    <div className="col-span-2">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={campaignFormData.use_ai_content}
                          onChange={(e) => setCampaignFormData({ ...campaignFormData, use_ai_content: e.target.checked })}
                          className="rounded"
                        />
                        <span className="text-sm text-gray-700 dark:text-gray-300">Use AI for Content Generation</span>
                      </label>
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowCampaignModal(false);
                        setEditingCampaign(null);
                        resetCampaignForm();
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      {editingCampaign ? 'Update' : 'Create'} Campaign
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* AI Generate Modal */}
        {showAIGenerateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                  <Sparkles className="w-6 h-6 text-purple-500" />
                  AI Content Generator
                </h2>
                <form onSubmit={handleGenerateAIContent} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Campaign *</label>
                    <select
                      required
                      value={aiGenerateData.campaign_id}
                      onChange={(e) => setAIGenerateData({ ...aiGenerateData, campaign_id: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="">Select Campaign</option>
                      {campaigns.map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Product (Optional)</label>
                    <select
                      value={aiGenerateData.product_id}
                      onChange={(e) => setAIGenerateData({ ...aiGenerateData, product_id: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="">Select Product</option>
                      {products.map(p => (
                        <option key={p.id} value={p.id}>{p.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Content Type</label>
                    <select
                      value={aiGenerateData.content_type}
                      onChange={(e) => setAIGenerateData({ ...aiGenerateData, content_type: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="poster">Poster/Image</option>
                      <option value="text">Text Post</option>
                      <option value="video">Video</option>
                      <option value="carousel">Carousel</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Prompt (Optional - AI will generate if empty)</label>
                    <textarea
                      value={aiGenerateData.prompt}
                      onChange={(e) => setAIGenerateData({ ...aiGenerateData, prompt: e.target.value })}
                      className="input-field w-full"
                      rows="3"
                      placeholder="Describe what you want to advertise..."
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Style</label>
                      <select
                        value={aiGenerateData.style}
                        onChange={(e) => setAIGenerateData({ ...aiGenerateData, style: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="creative">Creative</option>
                        <option value="modern">Modern</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Tone</label>
                      <select
                        value={aiGenerateData.tone}
                        onChange={(e) => setAIGenerateData({ ...aiGenerateData, tone: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="friendly">Friendly</option>
                        <option value="formal">Formal</option>
                        <option value="humorous">Humorous</option>
                        <option value="persuasive">Persuasive</option>
                      </select>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={aiGenerateData.generate_image}
                        onChange={(e) => setAIGenerateData({ ...aiGenerateData, generate_image: e.target.checked, generate_multiple_posters: e.target.checked ? false : aiGenerateData.generate_multiple_posters })}
                        className="rounded"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Generate AI Image</span>
                    </div>
                    {aiGenerateData.generate_image && (
                      <div className="grid grid-cols-2 gap-4 ml-6">
                        <div>
                          <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Image Width</label>
                          <input
                            type="number"
                            value={aiGenerateData.image_width}
                            onChange={(e) => setAIGenerateData({ ...aiGenerateData, image_width: parseInt(e.target.value) || 1024 })}
                            className="input-field w-full"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Image Height</label>
                          <input
                            type="number"
                            value={aiGenerateData.image_height}
                            onChange={(e) => setAIGenerateData({ ...aiGenerateData, image_height: parseInt(e.target.value) || 1024 })}
                            className="input-field w-full"
                          />
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={aiGenerateData.generate_multiple_posters}
                        onChange={(e) => setAIGenerateData({ ...aiGenerateData, generate_multiple_posters: e.target.checked, generate_image: e.target.checked ? false : aiGenerateData.generate_image })}
                        className="rounded"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">Generate Multiple Posters Automatically</span>
                    </div>
                    {aiGenerateData.generate_multiple_posters && (
                      <div className="ml-6">
                        <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Number of Posters (1-10)</label>
                        <input
                          type="number"
                          min="1"
                          max="10"
                          value={aiGenerateData.poster_count}
                          onChange={(e) => setAIGenerateData({ ...aiGenerateData, poster_count: parseInt(e.target.value) || 3 })}
                          className="input-field w-full"
                        />
                        <p className="text-xs text-gray-500 mt-1">AI will create multiple poster variations with different styles</p>
                      </div>
                    )}
                    
                    {aiGenerateData.content_type === 'video' && (
                      <>
                        <div className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={aiGenerateData.generate_video}
                            onChange={(e) => setAIGenerateData({ ...aiGenerateData, generate_video: e.target.checked })}
                            className="rounded"
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Generate AI Video</span>
                        </div>
                        {aiGenerateData.generate_video && (
                          <div className="ml-6">
                            <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Video Duration (seconds, 5-60)</label>
                            <input
                              type="number"
                              min="5"
                              max="60"
                              value={aiGenerateData.video_duration}
                              onChange={(e) => setAIGenerateData({ ...aiGenerateData, video_duration: parseInt(e.target.value) || 15 })}
                              className="input-field w-full"
                            />
                            <p className="text-xs text-gray-500 mt-1">AI will create an animated promotional video</p>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAIGenerateModal(false);
                        setAIGenerateData({
                          campaign_id: '',
                          product_id: '',
                          content_type: 'poster',
                          prompt: '',
                          style: 'professional',
                          tone: 'friendly',
                          generate_image: false,
                          generate_video: false,
                          generate_multiple_posters: false,
                          poster_count: 3,
                          image_width: 1024,
                          image_height: 1024,
                          video_duration: 15,
                        });
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary" disabled={generating}>
                      {generating ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></div>
                          Generating...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Generate Content
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Content Modal */}
        {showContentModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                  {editingContent ? 'Edit Content' : 'Create Content'}
                </h2>
                <form onSubmit={handleCreateContent} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Campaign *</label>
                      <select
                        required
                        value={contentFormData.campaign_id}
                        onChange={(e) => setContentFormData({ ...contentFormData, campaign_id: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">Select Campaign</option>
                        {campaigns.map(c => (
                          <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Content Type</label>
                      <select
                        value={contentFormData.content_type}
                        onChange={(e) => setContentFormData({ ...contentFormData, content_type: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="poster">Poster/Image</option>
                        <option value="video">Video</option>
                        <option value="text">Text Post</option>
                        <option value="carousel">Carousel</option>
                        <option value="story">Story</option>
                      </select>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Title</label>
                      <input
                        type="text"
                        value={contentFormData.title}
                        onChange={(e) => setContentFormData({ ...contentFormData, title: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Description</label>
                      <textarea
                        value={contentFormData.description}
                        onChange={(e) => setContentFormData({ ...contentFormData, description: e.target.value })}
                        className="input-field w-full"
                        rows="4"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Headline</label>
                      <input
                        type="text"
                        value={contentFormData.headline}
                        onChange={(e) => setContentFormData({ ...contentFormData, headline: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Call to Action</label>
                      <input
                        type="text"
                        value={contentFormData.call_to_action}
                        onChange={(e) => setContentFormData({ ...contentFormData, call_to_action: e.target.value })}
                        className="input-field w-full"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Hashtags</label>
                      <input
                        type="text"
                        value={contentFormData.hashtags}
                        onChange={(e) => setContentFormData({ ...contentFormData, hashtags: e.target.value })}
                        className="input-field w-full"
                        placeholder="#promotion #sale #offer"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Product (Optional)</label>
                      <select
                        value={contentFormData.product_id}
                        onChange={(e) => setContentFormData({ ...contentFormData, product_id: e.target.value })}
                        className="input-field w-full"
                      >
                        <option value="">Select Product</option>
                        {products.map(p => (
                          <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                      </select>
                    </div>
                    <div className="col-span-2">
                      <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Upload Image</label>
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          if (e.target.files[0]) {
                            setContentFormData({ ...contentFormData, image: e.target.files[0] });
                            const reader = new FileReader();
                            reader.onloadend = () => {
                              setImagePreview(reader.result);
                            };
                            reader.readAsDataURL(e.target.files[0]);
                          }
                        }}
                        className="input-field w-full"
                      />
                      {imagePreview && (
                        <div className="mt-2">
                          <img src={imagePreview} alt="Preview" className="max-w-full h-48 object-cover rounded-lg" />
                        </div>
                      )}
                      {editingContent && editingContent.image && !imagePreview && (
                        <div className="mt-2">
                          <img src={editingContent.image} alt="Current" className="max-w-full h-48 object-cover rounded-lg" />
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowContentModal(false);
                        setEditingContent(null);
                        resetContentForm();
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      {editingContent ? 'Update' : 'Create'} Content
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Post Modal */}
        {showPostModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Publish to Social Media</h2>
                <form onSubmit={handlePublishPost} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Content *</label>
                    <select
                      required
                      value={postFormData.content_id}
                      onChange={(e) => setPostFormData({ ...postFormData, content_id: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="">Select Content</option>
                      {contents.filter(c => c.is_approved).map(c => (
                        <option key={c.id} value={c.id}>{c.title || 'Untitled'}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Social Account *</label>
                    <select
                      required
                      value={postFormData.social_account_id}
                      onChange={(e) => setPostFormData({ ...postFormData, social_account_id: e.target.value })}
                      className="input-field w-full"
                    >
                      <option value="">Select Account</option>
                      {socialAccounts.filter(a => a.is_connected).map(a => (
                        <option key={a.id} value={a.id}>{a.platform} - {a.account_name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Caption</label>
                    <textarea
                      value={postFormData.caption}
                      onChange={(e) => setPostFormData({ ...postFormData, caption: e.target.value })}
                      className="input-field w-full"
                      rows="4"
                      placeholder="Post caption (optional - will use content description if empty)"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Schedule Post (Optional)</label>
                    <input
                      type="datetime-local"
                      value={postFormData.scheduled_time}
                      onChange={(e) => setPostFormData({ ...postFormData, scheduled_time: e.target.value })}
                      className="input-field w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">Leave empty to publish immediately</p>
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowPostModal(false);
                        resetPostForm();
                      }}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn-primary">
                      <Share2 className="w-4 h-4 mr-2" />
                      {postFormData.scheduled_time ? 'Schedule' : 'Publish'} Post
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Poster View Modal */}
        {viewingPoster && viewingPoster.image && (
          <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4" onClick={() => setViewingPoster(null)}>
            <div className="relative max-w-7xl w-full max-h-[95vh] flex flex-col">
              <button
                onClick={() => setViewingPoster(null)}
                className="absolute top-4 right-4 z-10 bg-white dark:bg-gray-800 text-gray-900 dark:text-white p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                title="Close"
              >
                <X className="w-6 h-6" />
              </button>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-4 flex justify-between items-center">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{viewingPoster.title || 'Poster'}</h3>
                  {viewingPoster.description && (
                    <p className="text-gray-600 dark:text-gray-300 mt-1">{viewingPoster.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <a
                    href={viewingPoster.image}
                    download={`${viewingPoster.title || 'poster'}_${viewingPoster.id}.png`}
                    className="btn-primary flex items-center gap-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </a>
                  <a
                    href={viewingPoster.image}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-secondary flex items-center gap-2"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="w-4 h-4" />
                    Open in New Tab
                  </a>
                </div>
              </div>
              <div className="flex-1 overflow-auto flex items-center justify-center bg-gray-100 dark:bg-gray-900 rounded-lg p-4" onClick={(e) => e.stopPropagation()}>
                <img
                  src={viewingPoster.image}
                  alt={viewingPoster.title || 'Poster'}
                  className="max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}

